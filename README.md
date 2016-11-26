# Escape-Evernote
Tool for escaping from Evernote to freedom of markdown files.

## What is it?

Simple python script for breaking Evernote export file (.enex) into separate markdown notes. It is also extracting images from enex and add them as markdown inline link to notes.

## How

```
usage: parse_enex.py [-h] [-d [DIRECTORY]] [-f [FILE]] [-a] [-r] [-v] [-q]
                     [-t] [-l LOG]

optional arguments:
  -h, --help            show this help message and exit
  -d [DIRECTORY], --directory [DIRECTORY]
                        directory in which you wish to work (default:
                        current folder)
  -f [FILE], --file [FILE]
                        Evernote archive file (.enex) (default: Test.enex)
  -a, --split_attachments
                        Create separate folder with attachments for each note
                        or [default] put all attachments prefixed in
                        /attachments folder (default: False)
  -r, --relative_path   Relative (or absolute) path for images (default: True)
  -v, --version         show program's version number and exit
  -q, --quiet           don't print status messages to stdout (default: True)
  -t, --tidy            remove temporary files (.xml, .tmp, .log) (default:
                        False)
  -l LOG, --log LOG, --logfile LOG
                        logs notes processing (default: parse_enex.log)
```

I have included sample Test.enex file so you can play with it. 

### ToDo

* add option to upload images to cloud - Dropbox, Google Drive - for portability and easier preview
* currently images are included ath the end of note.  add option to place them where they had been originally.
* better README.md

## Why

* [Evernote raised it's prices and limited it's free tier to two devices](https://blog.evernote.com/blog/2016/06/28/changes-to-evernotes-pricing-plans/). - Looks like classic mob strategy. Not a nice feeling when your personal notes are kept hostage by en enforcer.  Put them in and then pay a ransom forever.

* [Evernote migrated to Google Cloud Platform](https://blog.evernote.com/blog/2016/09/13/evernotes-future-cloud/) - so you may have reservations about privacy of your notes.  

Ain't Google scanning your notes right now and connecting with other metadata information about? [They say they don't](https://help.evernote.com/hc/en-us/articles/226885427-FAQ-About-Migration-to-Google-Cloud-Platform). But hey, it's Google right?

## Credits and similiar projects

* Large portion of code comes originally from Ian Mortimer's blog - [kicking the evernote habbit](https://ianmorty.co.uk/kicking-the-evernote-habbit.html)
* I have used this [fork](https://github.com/dougdiego/ever2simple) of popular ever2simple project - [Exporting Evernote to Markdown](https://diego.org/2016/08/31/exporting-evernote-to-markdown/)
* I like [zzyzx](https://github.com/ambv/zzyzx) for migrating/backing up Apple Notes  - different story
