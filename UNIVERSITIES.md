# Universities

[Jump to supported universities](#fully-supported-universities)



## Adding support for your university

In order to support your university, some information is first needed.



### Necessary data to add support

In summary, the following information is needed:

- **University name** (e.g. *University of Central Lancashire*).
- **Short name** or abbreviation (e.g. *UCLan*).

- **Link to Blackboard portal** (e.g. *https://portal.uclan.ac.uk*).
- **Landing URL** after successfully logging in (e.g. *https://portal.uclan.ac.uk/ultra*).



> There are [other fields](#advanced-fields) you can collect but I strongly suggest you skip these



### Ready to contribute?

Please create an issue using [the following form][support-issue]. You will need a GitHub account to do so.

If you'd rather not create one, feel free to reach me at bbsync@san.contact with these details.



## Fully Supported Universities

- University of Central Lancashire



## Universities with Basic Support

These universities should be supported, but may be unstable in rare cases.

### Europe

#### British Isles

- University of Westminster
- University of Reading
- University of West Anglia
- Durham University
- University of Salford
- University of South Wales
- University of Leicester
- Imperial College London
- University of Bristol
- University of Sheffield
- Buckinghamshire New University
- University of Northampton
- University of Bedfordshire
- Leeds Beckett University
- Trinity College Dublin
- Cardiff University
- Sheffield Hallam University
- University of the West of England
- Northumbria University
- Ulster University

#### Mainland Europe

- Universidad Europea Madrid
- Universidad de Alcala

### North America

- University of Arkansas
- The George Washington University
- Alaska Pacific University
- Youngstown State University
- Ohio University
- Post University
- The University of Alabama
- Georgian College

### South America

- Universidad del Valle de Mexico
- Universidad Tecnologica ECOTEC
- Universidad Regional del Sureste
- Universidad de Palermo
- Universidad Tecnologica del Salvador
- Universidad Ana G. Mendez

### Asia

- Princess Nourah Bint Abdulrahman University


### Australia

- Torrens University
- Holmes Institute

If any information here seems wrong, please let me know in the issues.



------



## Footnotes



#### Advanced fields

- **Valid Blackboard data sources**

This is a tricky one because it can potentially help filter out dummy courses and other folders with no user content.

However, its usage may vary per institution, ultimately is not necessary, and if set incorrectly it may cause other users to not see any course at all.

You are fine without it and it is suggested to be skipped. If you have more information about how these are set internally, please let me know.

> To know this, you'll need to login to blackboard on a browser, and then visit the
> endpoint "/learn/api/public/v1/users/me/courses" on your university blackboard page.
> For instance, this might be: "https://portal.uclan.ac.uk/learn/api/public/v1/users/me/courses".
>
> Once on this page, you will see the list of courses you are registered for. Entries are of this form:

> ```json
> {
>   "id":"...",
>   "userId":"...",
>   "courseId":"...",
>   "dataSourceId":"_21_1",
>   "created":"...",
>   "modified":"...",
>   "availability":{"available":"Yes"},
>   "courseRoleId":"Student",
>   "lastAccessed":"..."
> }
> ```

>  Check the dataSourceId for all the entries returned and note down the one that appears most.

- **Possible `isp` and `org` fields** that would indicate a connection from an IP that belongs to the university.

In future releases, it might be possible to optimise the setup process by automatically detecting connections from a university ISP.

This, however, is yet to be implemented, and I would like to know your thoughts about it.

> Visit http://ip-api.com/json?fields=org,isp from an IP belonging to the institution and record those values.

[support-issue]: https://github.com/jacobszpz/BlackboardSync/issues/new?assignees=jacobszpz&labels=uni-support&projects=&template=unisupport.yml&title=%5BUniversity+Support%5D%3A+
