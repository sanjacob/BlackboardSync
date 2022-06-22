# Universities



## Adding support for your university

In order to support your university, some information is first needed.



### Necessary data to add support

In summary, the following information is needed:

- **University name** (e.g. *University of Central Lancashire*).
- **Short name** or abbreviation (e.g. *UCLan*).



For the login process:

- **Link to Blackboard portal** (e.g. *https://portal.uclan.ac.uk*).
- **Landing URL** after successfully logging in (e.g. *https://portal.uclan.ac.uk/ultra*).
- DOM Selectors for **username** and **password** inputs.
  - See [querySelector][querySelector], `#id` selectors vastly preferred.




For downloading files:

- **Valid Blackboard data sources** (don't bother with these for now).



For the automatic institution detection based on IP:

- **Possible `isp` and `org` fields** that would indicate a connection from an IP that belongs to the university.
   - Visit http://ip-api.com/json?fields=org,isp from an IP belonging to the institution and record those values.




### Ready to contribute?

Please create an issue using [the following template][support-issue].



## List of Supported Universities

- University of Central Lancashire




[querySelector]: https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector
[support-issue]: #todo
[login-issue]: #todo