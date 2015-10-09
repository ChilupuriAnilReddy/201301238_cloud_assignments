
if [ -z "$1" ]
  then
    echo "No Proper argument"
else
	java -cp "LIbrarys/*:" ProcessResume $1 $2  
fi

