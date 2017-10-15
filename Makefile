build:
	docker build -t alexgleith/gdal .

get-grids:
	-mkdir -p ./grids
	wget https://s3-ap-southeast-2.amazonaws.com/transformationgrids/GDA94_GDA2020_conformal.gsb \
		-O ./grids/GDA94_GDA2020_conformal.gsb
	wget https://s3-ap-southeast-2.amazonaws.com/transformationgrids/A66_National_13_09_01.gsb \
		-O ./grids/A66_National_13_09_01.gsb
	wget https://s3-ap-southeast-2.amazonaws.com/transformationgrids/National_84_02_07_01.gsb \
		-O ./grids/National_84_02_07_01.gsb
	wget https://s3-ap-southeast-2.amazonaws.com/transformationgrids/GDA94_GDA2020_conformal_and_distortion.gsb \
		-O ./grids/GDA94_GDA2020_conformal_and_distortion.gsb
