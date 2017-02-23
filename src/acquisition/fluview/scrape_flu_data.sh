#Google Flu Trends (RIP)
#GFT=flu_data/gft_`date "+%Y-%m-%d-%H"`.csv
#curl http://www.google.org/flutrends/us/data.txt | tail -1 > $GFT

URL=https://gis.cdc.gov/grasp/fluview/FluViewPhase2CustomDownload.ashx
ALL_SEASONS="64%2C63%2C62%2C61%2C60%2C59%2C58%2C57%2C56%2C55%2C54%2C53%2C52%2C51%2C50%2C49%2C48%2C47%2C46%2C45%2C44%2C43%2C42%2C41%2C40%2C39%2C38%2C37"
TIMESTAMP=`date "+%Y-%m-%d-%H"`
DATADIR=flu_data

#National
curl --data "SubRegionsList=&RegionID=3&SeasonsList=$ALL_SEASONS&DataSources=ILINet" $URL > data.zip
unzip data.zip
FV_NAT=$DATADIR/ili_nat_$TIMESTAMP.csv
cat ILINet.csv | tail -52 > $FV_NAT # save only the most recent 52 weeks
rm data.zip ILINet.csv

#HHS Regions
curl --data "SubRegionsList=1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10&RegionID=1&SeasonsList=$ALL_SEASONS&DataSources=ILINet" $URL > data.zip
unzip data.zip
FV_HHS=$DATADIR/ili_hhs_$TIMESTAMP.csv
cat ILINet.csv | tail -520 > $FV_HHS # save only the most recent 52 weeks
rm data.zip ILINet.csv

#Census Regions
curl --data "SubRegionsList=1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C9&RegionID=2&SeasonsList=$ALL_SEASONS&DataSources=ILINet" $URL > data.zip
unzip data.zip
FV_CEN=$DATADIR/ili_cen_$TIMESTAMP.csv
cat ILINet.csv | tail -468 > $FV_CEN # save only the most recent 52 weeks
rm data.zip ILINet.csv

#Database loader: epidata.fluview
python3 epidata/fluview/load_epidata_fluview.py $FV_NAT
python3 epidata/fluview/load_epidata_fluview.py $FV_HHS
python3 epidata/fluview/load_epidata_fluview.py $FV_CEN
