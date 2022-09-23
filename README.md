# ftp deep download
Deep download for ftp-type website. The website should be ftp type (e.g. search google with "ftp index of /").
It scans the folder structure of the url-source location. Then, it creates the same folder-structure on the local machine.
It downloads all files from the source and maintain the file name and folder structure. Multiple download (up to 10000 times) onto the same folder is fine.
It will not replace the existing file. The download log is saved in sqlite database. The keyboard interrupt event is supported.
If download fails, the status and the website that cause the failure will (in most cases) be saved in the database file.<br><br>
Enjoy deep downloading . . .<br><br>
<br>Tested and worked on (as of Sep 22, 2022)
* http://www.epncb.oma.be/ftp/data/format/
* https://www.ietf.org/ietf-ftp/ietf-mail-archive/73all/
* http://ftp.sun.ac.za/ftp/pub/documentation/debian/package_building/
* https://fernbase.org/ftp/Salvinia_cucullata/Salvinia_asm_v1.2/chloroplast_genome/
* https://mirbase.org/ftp/7.0/

<br>Strangely worked on
* http://ftp.sun.ac.za/ftp/pub/documentation/C-programming/

<br>Strangely failed on (infinite loop)
* https://dlink-me.com/ftp/OMNA/
* &nbsp;&nbsp;Get status 406 to just read the html

Known to not work on
* Not ftp type: https://github.com/Logan1x/Python-Scripts/
* http://ftp.sun.ac.za/ftp/pub/documentation/
* &nbsp;&nbsp;Get to a web page after clicking a folder, instead of reaching to the folder of multiple files
* &nbsp;&nbsp;Get "None" type
* http://ftp.sun.ac.za/ftp/pub/documentation/network/
* &nbsp;&nbsp;Contain the link to external website

## Example of the website that this deep download can work on

![ftp_type](https://user-images.githubusercontent.com/26897526/191877012-f94c574e-510b-450f-bd5b-f6a7ed06fe9a.png)
## Example of the screenshot

![DeepDownload](https://user-images.githubusercontent.com/26897526/191877039-9d860d41-8083-44f4-9fd5-0addabe21aa2.png)
