# ###################################################################################
# Script:     runner.ps1
# ###################################################################################

clear

# ###################################################################################
# ###################################################################################

cd libraries

python runner.py $args

cd ..

$Continue = Read-Host -Prompt 'Press Return to Continue'

# ###################################################################################
