#!/bin/bash
for filename in *.txt;
do
	encoding=$(file "$filename" | grep -o ASCII);
	if [[ ! -f "$encoding" ]]; then
		#echo $filename;
		iconv -c -f "$encoding" -t "utf-8" "$filename" -o "$filename"
	fi;
done;
