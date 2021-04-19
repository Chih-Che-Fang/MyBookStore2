REM release AWS resources
aws ec2 delete-security-group --group-name MyBookStore32144321
for /f "tokens=*" %%a in (ids.txt) do (
  aws ec2 terminate-instances --instance-ids %%a
)
aws ec2 delete-key-pair --key-name 677kp32144321

REM Delete temporary files
del 677kp32144321.pem
del instance.json
del ids.txt
del ips.txt