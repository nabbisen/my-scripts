set fname (string replace '.sass' '.styl' 'param.sass'); echo $fname
cd sass; for i in *; mkdir -p ../dest/$i; cd $i; for j in *; set fname (string replace '.sass' '.styl' $j); cp $j ../../dest/$i/$fname; end; cd ../; end; cd ../;
