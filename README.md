This package provides various utilities for automation at KTH. It
provides the following modules:

  - kthutils.ug  
    Access the UG editor through Python.

  - kthutils.participants  
    Read expected course participants through Python.

  - kthutils.iprange  
    Read IP ranges for computers in lab rooms.

  - kthutils.forms  
    Read forms data (CSV) from KTH Forms.

  - kthutils.stayawhile  
    Access the Stay A While queue API.

  - kthutils.onedrive
    Read, write, browse, and publish content in KTH OneDrive and
    SharePoint.

We also provide a command-line interface for the modules. This means
that the functionality can be accessed through both Python and the
shell.

#### OneDrive and SharePoint

The `kthutils onedrive` commands reuse the shared Ladok3 login session,
so no separate cookie import or login bootstrap is needed.

Supported URL forms include:

  - full SharePoint and OneDrive URLs
  - SharePoint copy links for files and folders
  - `Forms/AllItems.aspx` folder URLs
  - shared links of the form `/shared?id=...`
  - `Doc2.aspx?sourcedoc=...` document links for downloads
  - server-relative paths such as `/sites/...` and `/personal/...`
  - shorthands such as `kth:site-name`, `kth-my:user_ug_kth_se`, and bare
    site or OneDrive names

Available `onedrive` commands include:

  - `kthutils onedrive ls URL`
  - `kthutils onedrive ls --long URL`
  - `kthutils onedrive tree URL [MAX_DEPTH]`
  - `kthutils onedrive folders URL [MAX_DEPTH]`
  - `kthutils onedrive get URL [OUTPUT]`
  - `kthutils onedrive put LOCAL_FILE URL`
  - `kthutils onedrive page publish SITE_URL HTML_FILE`

Examples:

``` bash
kthutils onedrive ls kth:example
kthutils onedrive tree "https://kth.sharepoint.com/sites/example/Shared%20Documents"
kthutils onedrive get "https://kth.sharepoint.com/sites/example/_layouts/15/Doc2.aspx?sourcedoc=%7B...%7D"
kthutils onedrive page publish kth:example update.html --page-name weekly-update --title "Weekly update"
```

The page-publishing command creates or updates a modern SharePoint page,
saves the HTML content as a draft rich-text canvas, and publishes it to
`SitePages`.

SharePoint URL parsing, browsing ideas, and page-publishing flow adapt
ideas from prototype scripts by Alexander Baltatzis.

#### An example

We want to add the user `dbosk` as teacher in the group

`edu.courses.DD.DD1317.20232.1.teachers`.

In Python, we would do

``` python
import kthutils.credentials
import kthutils.ug

ug = kthutils.ug.UGsession(*kthutils.credentials.get_credentials())

group = ug.find_group_by_name("edu.courses.DD.DD1317.20232.1.teachers")
user = ug.find_user_by_username("dbosk")

ug.add_group_members([user["kthid"]], group["kthid"])
```

In the shell, we would do

``` bash
kthutils ug members add edu.courses.DD.DD1317.20232.1.teachers dbosk
```

#### Installation and documentation

Install the tools using `pip`:

``` bash
python3 -m pip install -U kthutils
```

You can read the documentation by running `pydoc` on the package:

``` bash
python3 -m pydoc kthutils
```
