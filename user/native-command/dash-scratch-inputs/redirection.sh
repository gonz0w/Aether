exec 3>/scratch/data
exec 4>&3
printf A >&3
printf B >&4
exec 3>&- 4>&-
/inputs/helper copy </scratch/data
