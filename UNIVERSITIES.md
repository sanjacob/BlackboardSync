# Universities

[Jump to supported universities](#supported-universities)


## Adding support for your university

In order to support your university, some information is first needed.


### Necessary data to add support

#### Basic Information

- **University name** (e.g. *University of Central Lancashire*).
- **Short name** or abbreviation (e.g. *UCLan*) if one exists.
- **Link to Blackboard portal** (e.g. *https://portal.uclan.ac.uk*).
- **Landing URL** after successfully logging in (e.g. *https://portal.uclan.ac.uk/ultra*).

#### Automatic Detection

In order to allow users to complete their setup process faster,
there is a built-in university detection system based on the
Internet Service Provider.
Note that this only works if you are currently connected to the
university network.
Fortunately, finding the required information is easy:

a. Visit our [automated checker][rdap-check] and note the result down.

b. **If** the automated checker is not working, follow these steps:

1. Find out your ip by visiting https://api.ipify.org/.
2. Visit https://rdap.org and enter your ip.
3. Note down the content of `Network Name`, `Country`, and `Remarks`.
   You can use `Ctrl+F` to find these fields.


> There are [other fields](#advanced-fields) you can collect but I strongly suggest you skip these


### Ready to contribute?

Please create an issue using [the following form][support-issue]. You will need a GitHub account to do so.

If you'd rather not create one, feel free to reach me at request@bbsync.app with these details.


## Supported Universities

These universities should be supported, but may be unstable in rare cases.

### Europe

#### British Isles

- University of Central Lancashire
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
- Edge Hill University
- University of Lincoln
- University of Aberdeen
- University of Derby
- University of Manchester
- University of York

#### Mainland Europe

- Universidad Europea Madrid
- Universidad de Alcala
- University of Antwerp
- Universidade do Minho
- Hanze University of Applied Sciences
- Centro Universitario de Tecnología y Arte Digital

### North America

- University of Arkansas
- The George Washington University
- Alaska Pacific University
- Youngstown State University
- Ohio University
- Post University
- The University of Alabama
- Georgian College
- Concordia University Wisconsin & Ann Arbor
- Sam Houston State University
- University of Connecticut
- Schoolcraft College
- Texas Tech University
- Seneca Polytechnic

### South America

- Universidad del Valle de Mexico
- Universidad Tecnologica ECOTEC
- Universidad Regional del Sureste
- Universidad de Palermo
- Universidad Tecnologica del Salvador
- Universidad Ana G. Mendez

### Asia

- Princess Nourah Bint Abdulrahman University
- The Chinese University of Hong Kong
- The Chinese University of Hong Kong, Shenzhen

### Australia

- Torrens University
- Holmes Institute
- University of Western Australia
- University of Otago
- Griffith University

### Africa

- University of Pretoria

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

[support-issue]: https://github.com/sanjacob/BlackboardSync/issues/new?assignees=sanjacob&labels=uni-new&projects=&template=uninew.yml&title=%5BNew+University%5D%3A+
[rdap-check]: https://74mxmsvvgqw6t23xycgaauf3cy0vyncw.lambda-url.eu-west-2.on.aws/
