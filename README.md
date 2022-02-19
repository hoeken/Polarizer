# Polarizer
Scripts for generating and manipulating sailing polars.  Currently works with B&G NMEA0183 over IP.

## Installation

Install required libraries:

~~~
pip3 install -r requirements.txt
~~~

## Data Collection:

You can assign an arbitrary name to your particular sail configuration and it will log all the raw data to a file.

~~~
./log-nmea0183-over-ip.py -c 'twin bow spin'
./log-nmea0183-over-ip.py -c 'bowsprit spin'
./log-nmea0183-over-ip.py -c 'screacher and full main'
./log-nmea0183-over-ip.py -c 'jib and full main'
./log-nmea0183-over-ip.py -c 'jib and first reef'
./log-nmea0183-over-ip.py -c 'jib and second reef'
~~~

## Polar Generation:

Afterwards, you can generate polars for each individual sail configuration and then combine them into a single 'best sailset' file.

~~~
./generate-polars.py -d 'data/screacher and full main' --tws_max=20 --twa_max=140
./generate-polars.py -d 'data/jib and full main'
./generate-polars.py -d 'data/jib and first reef'
./generate-polars.py -d 'data/twin bow spin' --twa_min=160
./generate-polars.py -d 'data/bowsprit spin' 

./combine-polars.py -a 'screacher and full main' -b 'jib and full main' -c 'jib and first reef' -d 'twin bow spin' -e 'bowsprit spin'
~~~

## Utility:

You can also manually choose what sail data to use for a particular TWA/TWS with the use of a legend file:

~~~
./legend-polars.py -l polars/combined-polars-legend.csv -s polars/combined-polars-sailset.csv
~~~

## Cleanup

Sometimes you might get some bad data that you want to trim out. Luckily, the log files are stored with a human readable timestamp, and each log entry is a single line. You can simply delete the offending lines if its at the beginning/end of a file, or split the files and cut the bag part out. For example if you forget to stop the script when you make a sail change, something goes wrong with the data collection, etc.

Simple bash script below for cutting out a portion of the log file. You will need to rename the files appropriately afterwards.
~~~
#file to be sliced
MYFILE=data/bowsprit\ spin\ test/stargazer-spin-bowsprit-n03.txt
START_TIMESTAMP=2022-01-08T00:20:00
END_TIMESTAMP=2022-01-08T01:09:00
#start time/line of the file to cut out
START_LINE=$(grep -n -m 1 $START_TIMESTAMP "$MYFILE" |sed  's/\([0-9]*\).*/\1/')
START_LINE=$(($START_LINE-1))
echo $START_LINE

#end time/line of the file to cut out
END_LINE=$(grep -n -m 1 "$END_TIMESTAMP" "$MYFILE" |sed  's/\([0-9]*\).*/\1/')
echo $END_LINE

#do the actual slicing
(head -$START_LINE > data/firstpart.txt) < "$MYFILE"
(head -$END_LINE > /dev/null; cat > data/lastpart.txt) < "$MYFILE"

#check the results...
./generate-polars.py -g -f data/firstpart.txt
./generate-polars.py -g -f data/lastpart.txt
~~~

Split files in to chunks of ### lines:

~~~
split --verbose -dl 300000 --additional-suffix=.txt "mydata.txt" "mydata-split"
~~~

