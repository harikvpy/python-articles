# Choosing a Python Web Framework
<cite>Hariharan Mahadevan(何瑞理), hari@smallpearl.com</cite>

## Background
In the previous [article](https://lsl.sinica.edu.tw/Blog/2023/10/evolution-of-web-frameworks/) we discussed what is a web framework and traced its evolutionary path to the current state. To reiterate what we discussed there, a web framework is a software library that supports the development of web sites and applications by providing reusable components to automate the common activities performed in web development such as database access, user management, access control, session management, etc.

Since there are tens (perhaps even more than hundred) of web frameworks out there, in this article we will discuss the general factors that ought to be considered before choosing one for a project. This article primarily aimed at decision makers who are not all that familiar with web development but have an understanding of technology. It will also appeal to the seasoned technocrat who is new to the world of web.

## How to choose a framework
Given the plethora of web frameworks that are available out there, how does one choose a framework for a given project? Though all the frameworks achieve the same thing, they have different strengths and weaknesses. Having some idea on these pros and cons will go some way in choosing a framework that is the right fit for your project. We start with a couple of factors that are more in the realm of management science and then move into the technology itself.

These factors are not in any order of importance. Each project and its constraints determine which of the following is more important than others.

### Availability of Skills
Having readily available programmer resources is one of the key factors in choosing a framework. If you have a bunch of developers who are well versed in a language, it makes perfect sense to choose a framework that is written using that language or a language that closely resembles it.

There are exceptions though. If the language is a compiled language such as C/C++, you might be hard pressed to find a framework that has enough deployments to justify it's selection. The next best thing you can do is pick a framework in a language that closely resembles the syntax of the language skills that you already have. In the example above, Python somewhat matches the syntax of C/C++. Basic programming constructs like control statements, loops & array declarations look and feel similar. So the developers do not have to start from scratch.

### Language popularity
Web frameworks come in a variety of languages. From legacy C/C++ to modern JavaScript. So how does one who is not familiar with programming languages choose a framework for a project and then build a team? A basic rule of thumb in this case is to choose a framework that uses a popular language. This will make it easy to find the necessary human resources to kick off the project and add resources when the project demands it.

A means of judging language popularity is to go by the results of surveys that are done routinely. StackOverflow and GitHub both do this annually. Some other sites use Google search metrics to publish *live* such results.

The following table lists the top popular programming languages as of Jan 2024. This result is based on Google search frequency for language keywords & tutorials. As you can see Python, Java & JavaScript occupy the top three spots. PHP & TypeScript(the strictly typed cousin of JavaScript) does not do all that well. Naturally one would be better off to choose a framework that employs one of Python, Java or JavaScript.

| Language | Share | 1-year trend |
|-----------|------|--------------|
| Python | 28.2 % | +0.5 % |
| Java | 15.73 % | -0.9 % |
| JavaScript | 8.91 % | -0.6 % |
| C/C++ | 6.8 % | -0.0 % |
| C# | 6.67 % | -0.3 % |
| R | 4.59 % | +0.6 % |
| PHP | 4.54 % | -0.7 % |
| TypeScript | 2.92 % | +0.2 % |
| Swift | 2.77 % | +0.6 % |

## Localized language popularity
The data above is based on statistics taken [globally](https://pypl.github.io/PYPL.html), which may not hold true for the local geography. For instance, if you look at the Taiwan web landscape, anecdotal evidence suggests that PHP is still extremely popular. But anecdotal evidence cannot be relied upon unless we really do not have any other data to rely on. In the absence of any official surveys, one metric could be to use the number of job postings in popular recruitment websites that require a specific programming language as a required skill.

The following table shows the results of searches from the popular local recruitment website `www.104.com.tw`. Searches were  done using the pattern `<programming-language> engineer` for each of the following languages.

| Language | # of job listings |
|----|---|
| PHP | 13653 |
| Python | 11151 |
| C# | 11051 |
| JavaScript | 11017 |
| C++ | 10521
| Java | 10061 |
| TypeScript | 6728 |
| Go | 8403 |
| R | 8210 |
| Rust | 6220 |

Going by the data above, the anecdotal evidence mentioned earlier holds true. PHP may not be popular worldwide, but it remains a popular language in Taiwan. In other words, lacking any other major influencing factors, in spite of PHP being low in the global popularity list, selecting a PHP based web framework may not be such a bad decision after all.

## Feature completeness
A web application is way more than a pretty layout. Typical web applications would require some form of user registration and login management. It has to have a way of composing a webpage using reusable pieces of code so that common features of different pages can be abstracted out into reusable HTML fragments.

Some of the essential capabilities of a web framework can be identified as:-

* Template language for HTML fragment reuse
* User & session management
* Database access via [ORM](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping)
* Access control
* JSON API generation
* Async programming constructs

Frameworks are typically of two kinds -- those that come fully loaded supporting all the above or those that come with the bare minimum and then offer each of the above as optional packages that you have to add & configure yourself. These optional packages are quite often not part of the original framework and are provided by independent third party projects.

Unless one has deep knowledge and expertise on web frameworks, a safe bet is to go with a framework that comes fully loaded with all the necessary features to develop a complete website. 

While examining each framework and identifying its compliance for the above criteria is beyond the scope of this article, the table below lists the most popular three Python frameworks with respect to their feature matrix. Note that almost all frameworks can support all the features above, but with the help of additional modules developed independently. The table only marks a feature compliance, if it is included in the base framework package.

| Framework  | Templates | User | ORM | Permissions | API | Async
|------------|--------------|------|---|-|-|-|
| [Django](https://djangoproject.com/) | <center>x</center> | <center>x</center> |<center>x</center> |<center>x</center> |<center>x</center> |  |
| [Flask](https://flask.palletsprojects.com/en/3.0.x/) | <center>x</center> | | | | |  |
| [FastAPI](https://fastapi.tiangolo.com/) |<center>x</center>|  | | | <center>x</center> | <center>x</center> |


## Framework maturity
A mature web framework is one that has not only been around for many years, but which has many active deployments in production sites. Perl was one of the earliest interpreted languages used to build websites. And there are a few Perl language based frameworks that have been around for a long time. However, the number of production sites that use a Perl based framework are quite miniscule when compared with other frameworks that use Python, Java or JavaScript.

A mature framework will tend to have less frequent major updates as opposed to a nascently developed one. However, it will be one which has an official organization (virtual or otherwise) consisting of a dedicated team of maintainers (as opposed to a few engineers). And major version updates should not result in too many breaking changes to existing code and should provide a migration path.

The table below lists the three most popular Python frameworks and their first and latest release dates.

| Framework  | First Release | Latest Release | Current Version |
|------------|---------------|---------------|----|
| Django     | May 8, 2012   | Jan 2 2024 | 5.0.1 |
| Flask      | Apr 27, 2018  | Jan 16 2024 | 3.0.1 |
| FastAPI    | Dec 16 2018   | Jan 9 2024 | 0.109.0 |

The table above ought to give you an idea on the level of maturity of these frameworks.

## Framework popularity
One measure of judging a frameworks popularity is count the number of production websites that use the framework. However this data is hard to come by. The frameworks' websites list some of the *live* sites that use it, but it cannot be exhaustive. A better metric would be to use the respective project's source code repository's star rating.

| Framework  | Star Rating | Forks | Watching |
|------------|-------------|-----|---|
| Django     | 75200  | 30800 | 2300 |
| FastAPI    | 67300  | 5700 | 655 |
| Flask      | 65500  | 16100 | 2100 |

This exhibits interesting statistics. In spite of having been released only 6 years ago, both Flask & FastAPI have a star rating that's pretty close to Django. Flask's *Watching* value is very close to Django's. One conclusion we can derive from this is that both Flask & FastAPI are very popular and probably going to become even more popular than Django in the coming years.

It also bears mentioning that both Flask & FastAPI are designed to address a specific niche market for which either Django was not a good fit or it was an overkill.

Flask was initially designed as a dead simple framework suited for simple websites that render HTML pages from templates. While Django provided this capability, Django also comes with a lot of additional packages that many thought was unnecessary for simple websites. Besides when a framework comes fully loaded, it is easy to get lost in the myriad amount of details that its documentation provides.

FasAPI, as the name suggests, is a pure async framework designed to create REST API endpoints. So if your requirement is to build a microservice or a server that exposes only REST API endpoints, FastAPI is a good choice. It chose async programming as the default model as API only servers are typically required to be immensely scalable and async programming helps you achieve that.

## Project domain & constraints
The project domain & its constraints are key influencing factors in choosing the right framework. This is best illustrated with an example or two.

Imagine the objective of the website is to allow its users to upload a few images (perhaps pictures from a microscope) that are to be analyzed by a set of libraries provided as a Python package. In this case it makes perfect sense to use a Python based web framework as that would allow quick and tight integration with the Python based image analysis library.

On the other hand, the image analysis could be done by a remote server only available via HTTP API and the analysis could take many seconds to even minutes to complete. In this case, ideally the chosen framework should support asynchronous programming so that many requests could be queued without each request freezing up the CPU. This principle was explained in detail, with working examples in a previous article [here](https://lsl.sinica.edu.tw/Blog/2023/08/async-python-part-2-a-deeper-look/).

And if the analysis could take hours to complete, an altogether different approach ought to be considered. One solution could be a framework that allows jobs to be submitted and the results to be notified offline via an email. Frameworks that use languages such as Go lend itself nicely to this kind of requirement.

However, if the project is to develop a microservices server that exposes a REST API for other clients and the number of clients could potentially reach hundreds of thousands, you should perhaps look at FastAPI seriously.

To summarize, the following table lists the overweighing project criteria factor and the framework that is suitable to achieve that criteria with relatively less effort.

| Key Requirement | Best Framework |
|-----------------|---|
| REST API | FastAPI |
| REST API, >100000 requests/sec | Fast API |
| Static Pages | Flask |
| Data storage/access | Django |
| Users with multilevel permissions | Django |

## Conclusion
I hope this discussion gave you a peek into the thought process that goes into the process of choosing a web framework for a project. The latter half of the article focused purely on Python based packages for a reason. Python is onoe of the most popular languages at present and is quite widely used in academic circles such as Sinica, one of whose library blogs this article is written for.

If you have any thoughts or opinions that differ from my viewpoint, feel free to email me directly. I would love to hear them and guarantee a response to each and every one.


*<small>Hariharan is a software developer turned entrepreneur running his own [software business](https://smallpearl.com) in Taiwan. He has over 30 years of hands-on development experience in domains ranging from device drivers to cloud based applications and still enjoys coding.</small>*
