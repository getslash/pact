Changelog
=========

* :feature:`-` remove deprecated ``PactBase.finished()`` API
* :feature:`-` write wait's duration seconds to log
* :feature:`-` Switch to PBR
* :release:`1.10.0 <15-10-2017>`
* :feature:`-` ``PactGroup`` raises custom timeout exception from child if available
* :release:`1.9.0 <6-8-2017>`
* :bug:`- major` Handle exceptions thrown in a 'during' callback
* :release:`1.8.0 <11-07-2017>`
* :feature:`-` Add lastly callbacks that are similar to 'then' but called afterwards
* :release:`1.7.0 <27-06-2017>`
* :feature:`18` Allow specifying overall deadlines for pacts and groups
* :release:`1.6.0 <15-12-2016>`
* :feature:`-` Allow PactGroup.wait to be eager (waiting for all pacts and not just the first one)
* :feature:`-` Add logging to failed ``then`` callbacks
* :release:`1.5.0 <29-08-2016>`
* :feature:`-` Make sure callbacks passed are callable
* :feature:`12` Added ``on_timeout`` handler
