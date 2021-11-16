#!/bin/bash

N=$1

# Clear the (per trialn) jsons ahead of time
echo "clearing folder/computing indexing.."
rm -rf bayestar_runs/*

rm -rf json_dump/*
rm -rf plots/*
rm -rf join are/*

RA_N=$N
DEC_N=$((N/2))

echo "N=$N : ra_n=$RA_N : dec_n=$DEC_N"
echo " "
echo " "

echo "looping..."
echo " "



for (( i=0; i<$RA_N ; i++));
do
    for (( j=0; j<$DEC_N ; j++));
    do
        echo "case: $i , $j"
        python3 runner.py --ra $i --dec $j --N $N &
        echo " "
        echo " "
    done 
    
done



echo "area output monitor.."
python3 monitor.py --directory "json_dump" --dir_length $(((RA_N)*(DEC_N)))

echo " "


echo "joining area outputs.."
python3 json_stack_keys.py --jsons_path "json_dump/" --merge_path_name "joined_area/joined_area"

echo " "
echo "making plots..."

python3 plot_maker.py


echo "done!"
