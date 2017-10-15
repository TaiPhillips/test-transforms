#!/usr/bin/env python3

import csv
import math
import os

import subprocess

import pyproj

from geojson import Feature, FeatureCollection, Point
import geojson


def write_coords_geojson(coords, outfilename):
    features = []
    for key, coord in coords.items():
        feature = Feature(geometry=Point(coord), properties={'id': key})
        features.append(feature)

    feature_collection = FeatureCollection(features)

    with open(outfilename, 'w') as outfile:
        geojson.dump(feature_collection, outfile)


def compare_coords(correct, test, source):
    dx = test[0] - correct[0]
    dy = test[1] - correct[1]

    angle = math.degrees(math.atan2(dx, dy))
    if angle - 360:
        angle = angle + 360

    diff = math.fabs(math.hypot(dx, dy))

    if diff > 0.1:
        print("From   : ", source)
        print("To true: ", correct)
        print("To tran: ", test)
        print("Diff is: {:0.3f} m in a {:0.0f} direction\n".format(diff, angle))
        return False
    else:
        return True

    # assert math.fabs(diff) < 0.1


work_dir = os.path.dirname(os.path.realpath(__file__))

test_coords_gda94_to_2020 = os.path.join(work_dir, "test_stations_coordiates_gda94_to_gda2020.csv")

GDA2020CONF_DIST = os.path.join(work_dir, 'grids/GDA94_GDA2020_conformal_and_distortion.gsb')

gda94_epsg = pyproj.Proj(init='EPSG:28355')
agd66_epsg = pyproj.Proj(init='EPSG:20255')
try:
    gda2020_epsg = pyproj.Proj(init='EPSG:7855')
except RuntimeError as e:
    print("Failed to load 2020 projection with error: {}".format(e))

gda94_gda2020_from = pyproj.Proj(
    proj='utm',
    zone=55,
    south=True,
    ellps='GRS80',
    towgs84='0,0,0,0,0,0,0',
    nadgrids=GDA2020CONF_DIST,
    units='m',
    no_defs=True,
    wktext=True
)
gda94_gda2020_to = pyproj.Proj(
    proj='utm',
    zone=55,
    south=True,
    towgs84='0,0,0,0,0,0,0',
    ellps='GRS80',
    units='m',
    no_defs=True,
    wktext=True
)

gda2020_coords = {}
gda94_coords = {}

with open(test_coords_gda94_to_2020, 'r') as file:
    reader = csv.reader(file, delimiter=',')
    next(reader)
    for row in reader:
        gda2020_coord = [float(row[1]), float(row[2])]
        gda94_coord = [float(row[11]), float(row[12])]
        key = row[0]

        gda2020_coords[key] = gda2020_coord
        gda94_coords[key] = gda94_coord

results = []
for key, coord in gda94_coords.items():
    gda20_coord = gda2020_coords[key]
    output = pyproj.transform(gda94_gda2020_from, gda94_gda2020_to, coord[0], coord[1])
    result = compare_coords(gda20_coord, output, coord)
    results.append(result)

print("\nSuccess with {} out of {} using pyproj.".format(sum(results), len(results)))


write_coords_geojson(gda94_coords, '/tmp/gda94.geojson')

ogr2ogr_command = (
    'ogr2ogr '
    '-s_srs "+proj=utm +zone=55 +south +ellps=GRS80 +units=m +no_defs +towgs84=0,0,0,0,0,0,0 +nadgrids=' + GDA2020CONF_DIST + ' +wktext" '
    '-t_srs "+proj=utm +zone=55 +south +ellps=GRS80 +units=m +no_defs +towgs84=0,0,0,0,0,0,0 +wktext" '
    '-f "GeoJSON" /tmp/gda20.geojson /tmp/gda94.geojson'
)

result = subprocess.call(ogr2ogr_command, shell=True)

data = None
with open('/tmp/gda20.geojson', 'r') as data_file:
    data = geojson.load(data_file)

results = []
for feature in data['features']:
    key = feature['properties']['id']
    gda94_coord = gda94_coords[key]
    gda20_coord = gda2020_coords[key]
    coord = feature['geometry']['coordinates']
    result = compare_coords(gda20_coord, coord, gda94_coord)
    results.append(result)

print("\nSuccess with {} out of {} using ogr2ogr.\n".format(sum(results), len(results)))
