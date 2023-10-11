"""
===============
=== Purpose ===
===============

Downloads CDC page stats stored in Delphi's dropbox.

This program:
  1. downloads new files within dropbox:/cdc_page_stats
  2. moves the originals to dropbox:/cdc_page_stats/archived_reports
  3. zips the downloaded files and moves that to delphi:/common/cdc_stage
  4. queues cdc_upload.py, cdc_extract.py, and other scripts to run

See also:
  - cdc_upload.py
  - cdc_extract.py
"""

# standard library
import datetime
from zipfile import ZIP_DEFLATED, ZipFile

# third party
import dropbox
import mysql.connector

# first party
import delphi.operations.secrets as secrets


# location constants
DROPBOX_BASE_DIR = "/cdc_page_stats"
DELPHI_BASE_DIR = "/common/cdc_stage"


def get_timestamp_string():
    """
    Return the current local date and time as a string.

    The format is "%Y%m%d_%H%M%S".
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def trigger_further_processing():
    """Add CDCP processing scripts to the Automation run queue."""

    # connect
    u, p = secrets.db.auto
    cnx = mysql.connector.connect(user=u, password=p, database="automation")
    cur = cnx.cursor()

    # add step "Process CDCP Data" to queue
    cur.execute("CALL automation.RunStep(46)")

    # disconnect
    cur.close()
    cnx.commit()
    cnx.close()


def fetch_data():
    """
    Check for new files on dropbox, download them, zip them, cleanup dropbox, and
    trigger further processing of new data.
    """

    # initialize dropbox api
    dbx = dropbox.Dropbox(secrets.cdcp.dropbox_token)

    # look for new CDC data files
    print(f"checking dropbox: {DROPBOX_BASE_DIR}")
    save_list = []
    for entry in dbx.files_list_folder(DROPBOX_BASE_DIR).entries:
        name = entry.name
        if name.endswith(".csv") or name.endswith(".zip"):
            print(f" download: {name}")
            save_list.append(name)
        else:
            print(f" skip: {name}")

    # determine if there's anything to be done
    if len(save_list) == 0:
        print("did not find any new data files")
        return

    # download new files, saving them inside of a new zip file
    timestamp = get_timestamp_string()
    zip_path = f"{DELPHI_BASE_DIR}/dropbox_{timestamp}.zip"
    print(f"downloading into delphi:{zip_path}")
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zf:
        for name in save_list:
            # location of the file on dropbox
            dropbox_path = f"{DROPBOX_BASE_DIR}/{name}"
            print(f" {dropbox_path}")

            # start the download
            meta, resp = dbx.files_download(dropbox_path)

            # check status and length
            if resp.status_code != 200:
                raise Exception(["resp.status_code", resp.status_code])
            dropbox_len = meta.size
            print(f"  need {int(dropbox_len)} bytes...")
            content_len = int(resp.headers.get("Content-Length", -1))
            if dropbox_len != content_len:
                info = ["dropbox_len", dropbox_len, "content_len", content_len]
                raise Exception(info)

            # finish the download, holding the data in this variable
            filedata = resp.content

            # check the length again
            payload_len = len(filedata)
            print("  downloaded")
            if dropbox_len != payload_len:
                info = ["dropbox_len", dropbox_len, "payload_len", payload_len]
                raise Exception(info)

            # add the downloaded file to the zip file
            zf.writestr(name, filedata)
            print("  added")

    # At this point, all the data is stored and awaiting further processing on
    # the delphi server.
    print(f"saved all new data in {zip_path}")

    # on dropbox, archive downloaded files so they won't be downloaded again
    archive_dir = f"archived_reports/processed_{timestamp}"
    print("archiving files...")
    for name in save_list:
        # source and destination
        dropbox_src = f"{DROPBOX_BASE_DIR}/{name}"
        dropbox_dst = f"{DROPBOX_BASE_DIR}/{archive_dir}/{name}"
        print(f" {dropbox_src} -> {dropbox_dst}")

        # move the file
        meta = dbx.files_move(dropbox_src, dropbox_dst)

        # sanity check
        if archive_dir not in meta.path_lower:
            raise Exception(f"failed to move {name}")

    # finally, trigger the usual processing flow
    print("triggering processing flow")
    trigger_further_processing()
    print("done")


def main():
    # fetch new data
    fetch_data()


if __name__ == "__main__":
    main()
