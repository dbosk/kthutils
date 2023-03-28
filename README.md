This package provides various utilities for automation at KTH. It
provides the following modules:

- `kthutils.ug`: Access the UG editor through Python.

We also provide a command-line interface for the modules. This means
that the functionality can be accessed through both Python and the
shell.

An example: We want to add the user `dbosk` as teacher in the group

  edu.courses.DD.DD1317.20232.1.teachers

In Python, we would do

```python
import kthutils.credentials
import kthutils.ug

ug = kthutils.ug.UGsession(*kthutils.credentials.get_credentials())

group = ug.find_group_by_name("edu.courses.DD.DD1317.20232.1.teachers")
user = ug.find_user_by_username("dbosk")

ug.add_group_members([user["kthid"]], group["kthid"])
```

In the shell, we would do

```bash
kthutils ug members add edu.courses.DD.DD1317.20232.1.teachers dbosk
```

Install the tools using `pip`:

```bash
python3 -m pip install -U kthutils
```
