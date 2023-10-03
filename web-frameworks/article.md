# Evolution of Web Frameworks
<cite>Hariharan Mahadevan(何瑞理), hari@smallpearl.com</cite>

## What is a Web Frameowrk
Web framework is a software framework designed to support the development of web sites and applications. They provide a standard way to build and deploy web applications and provide software tools to automate the overhead associated with common activities performed in web development such as database access, user management, access control, session management, etc. The fundamental objective of a web framework is to promote code reuse by reducing repetitive tasks into a common set of reusable components.

In this article, we will trace the evolution of web frameworks from its early days to its current form, while identifying the reasons for the transition in technology. As there are literally hundreds of web frameworks, covering all of which is impractical, we will only be using major transition points in the technology trends.

## Early days
In its very early days, the Web consisted of a web server (CERN httpd and later Apache) that listened for requests from clients such as Netscape & Mozilla and returned an HTML response. The servers could be configured such that based on different request paths, it would return different responses. This was fine for static content such as documents or chapters of a book. For example different documents could be indexed by by different request paths and similarly different chapters could be index by the chapter number, thereby allowing the client to retrieve the document or chapter of interest directly. This path organization also helped reduce the amount of data being transferred resulting in better response times.

But as the web became interactive, whereby it allowed users to input data and the response had to be dynamically generated based on the input, this mechanism of serving statically defined pages became quite limiting.

## CGI
The response from the server designers to accommodate this requirement was to allow external programs to be executed from the server. Such external programs are passed certain arguments (via the standard program command line) and its response, written to <i>stdout</i>, is returned back to the client as the response. Arguments included data that is input by the user in the browser (supplied as form data) alongwith additional standard arguments such as cookies, session identifier, request origin, browser language, etc. The response would typically be complete HTML pages that the browser can render as if it came from a static content. The type, content & structure of the arguments that were passed to the external programs and their response was standardized and this standard was referred as CGI or Common Gateway Interface. Standardization allowed engineers to choose between different standards compliant servers in search for higher efficiency & scalability.

CGI brought dynamism to the otherwise static web. Also, since these were pure processes, they could be written in any language. C, C++, Java, Python, Perl, you name it. Even as a shell script! As long as the language allowed you to parse the command line arguments and write back to the stdout, it could be used to write a CGI script.

CGI, however, also had two major drawbacks.

Since each script was executed as a separate process as and when the request came in, it became quite resource intensive. This is because creating a new process is a very expensive operation -- both in terms of memory and CPU. It was observed that often times the initial setup expense of a script far exceeded the cost of the actual computation done by it. As the web grew exponentially and consequently the number of HTTP requests handled by a server grew, CGI as a means of providing interactivity to the web proved to be not a scalable solution.

Another big drawback of CGI was security, or lack thereof. Since the CGI programs are processes launched by the web servers, they inherit the security context of its parent process, the web server. So if a web server is running with the highest OS privileges (as was often the case) the CGI script will also be run as a high privilege process. Since user input (typically form input from the browser) was passed directly to the CGI programs, attackers found ways to embed commands in this input and cause these commands to execute at the server resulting in serious security breaches.

## Apache Server Modules (mods)
One of the solutions to address the scalability issues that plagued CGI was to extend the server via Multiprocessing Server Modules or <i>server mods</i>. Mods are dynamically loadable modules to which requests can be delegated from the main server. Mods can handle the requests either by launching new processes or separate threads as per the mod's design. Once the request is processed, mods would send the response back to the core server which then sends it back to the client.

Though MPM sounds like a generic term, it was first developed by Apache and one of their first implementations was <i>mod_perl</i>, a module that allowed [Perl](https://www.perl.org/) scripts to be executed from within the Apache server without having to start a Perl interpreter for each incoming request. The same design approach was later adopted in other servers such as [NGINX](https://www.nginx.com/).

Note that by convention MPMs are named with the prefix <i>mod_</i> followed by the mod's name.

Another benefit of <i>mod_perl</i> was that it could emulate a CGI environment, which allowed existing Perl CGI scripts to be executed resulting in a performance boost while help retain them without having to be re-written. Since PHP, one of the first dedicated web framework languages, was written in Perl, mod_php could be developed leveraging on the embedded Perl engine and that too resulted in achieving great scalability improvements over a pure CGI approach.

## FastCGI
Another solution to address the scalability issues, was FastCGI. In FastCGI, instead of creating a separate process for each external script, it uses a persistent process to serve multiple requests. The HTTP server and the FastCGI process communicate via a Unix or TCP socket. The incoming request details, that were earlier passed as arguments to the CGI script, are now passed to the FastCGI script via the socket connection. The response from the script, received via the same socket connection is then relayed back to the browser client.

Note that using a socket connection allows multiple requests to be handled simultaneously by making multiple connections to the FastCGI process or by launching multiple FastCGI processes (each bound to a different socket, conforming to predefined range of port numbers) or a combination of both.

Since new processes need not be created for each incoming request, this addressed the scalability issues faced by the CGI mechanism. Besides, being a socket connection, the FastCGI process could be run in a different security context than the webserver thereby improving the security risks of the CGI approach.

Another benefit of separating the FastCGI process from the web server is that these processes can be independently restarted after an update (or to reclaim memory caused by leaks) without resulting in total outage to the static portions of the website.

## Software Design Patterns
The idea behind design patterns is to divide software application's various elements into specific contexts so as to bring clarity to the overall application design. Once an element's context is clear, its goal can be clearly defined which in turn will help define its inputs & outputs.

As the web grew, web applications became more and more complex. Consequently, software design patterns that helped manage the complexity of large software application inevitably made its way into web applications too. Design patterns such as [Model-View-Controller](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) that were used to bring clarity into large-scale software applications were applied to web frameworks.

As web applications started being architected & designed at a high level using design patterns, it became evident that languages such as Perl, which hitherto were being used to provide dynamism to websites, are inadequate. More expressive programming languages were required to translate the design into code that captured the pattern as closedly as possible. This is the genesis for the many modern web frameworks that we see today. Multiple frameworks some using different languages and some using the same language started evolving. Some prominent examples(just a random sampling and by no means exhaustive) are [ASP.NET](https://dotnet.microsoft.com/en-us/apps/aspnet), [Jakarta](https://jakarta.ee/), [Ruby on Rails](https://rubyonrails.org/) and [Django](https://djangoproject.com).

While some of these frameworks use the MVC pattern, others such as Django employ what is called a MVT (Model-View-Template) pattern. But the idea is the same -- provide clear context to different portions of the code and assign specific roles & responsibilities to each context, resulting in consistent design throughout a large application codebase.

Besides scalability, the advantage of these frameworks is the minimum security that they guarantee. By forcing the application to fit within the framework, web applications inherit the minimum security guarantees that the framework offers. For instance, most of these frameworks, by default require production sites to be served over HTTPS. Also, operations that result in changes to the backend data require additional precautions (often provided by default by the framework) in the code all but eliminating risks posed by common low-cost attacks by hackers -- [Cross Site Scripting](https://en.wikipedia.org/wiki/Cross-site_scripting) & [Cross-site request forgery](https://en.wikipedia.org/wiki/Cross-site_request_forgery) being two of them.

## AJAX & jQuery
While neither AJAX nor jQuery are true frameworks, they merit a special mention in our discussion on the evolution of web frameworks.

As web applications became more interactive, the browser side application UI became more & more complex. Complex UI requires continuous interaction with the backend to retrieve context sensitive data that is related to the user input. For example a user searching for a street should only have to enter the first few letters of the street name and the UI should respond by listing all streets that match the letters input by the user.

Delivering such complex & time sensitive UI interaction by pre-rending the entire webpage would require enormous resources from the server. A more efficient approach would be to query the server for the relevant data (in this case street names matching the user input) and use the values returned to modify the HTML page already rendered by a previous full page request's response.

In order to facilitate this browsers, provided a dedicated JavaScript API to send a background request to the server and process the results. Browsers also allowed such JavaScript code to modify the displayed HTML page contents by adding new HTML elements or removing and amending existing HTML tags.

This dedicated API is often referred to as [AJAX](https://en.wikipedia.org/wiki/Ajax_(programming)). AJAX requests to server often, though not necessarily, yielded responses that consited of JavaScript objects encoded in [JSON](https://en.wikipedia.org/wiki/JSON). These JSON responses could be directly loaded into JavaScript converting them into valid JavaScript objects and worked upon.

Whereas AJAX provides a standard way to retrieve data from a remote in the background, adding & modifying the HTML page using the plain JavaScript API bundled with the browser was proving to be a pain. Enter [jQuery](https://jquery.com/). jQuery provided a fast & small library of wrapper functions that made the job of finding, modifying & adding HTML elements a breeze.

Together these two key innovations suddenly made web applications closer than ever to their statically deployed counterparts.

However AJAX & jQuery were not without their drawbacks. Server logic became increasingly complex as it now consisted of two kinds of response types. Some requests resulted in full HTML pages being returned whereas other requests returned pure data encoded as JSON. Of course, given the choice, developers would prefer to standardize all the responses to JSON as it's the simpler of the two. This line of thought along with the quest for ever increasing server scalability led to the next transition in the evolution of web frameworks.

## JavaScript Frontend Frameworks
Although the MVC pattern frameworks made rapid improvements to quality of web applications, quest for higher scalability resulted in another trend -- JavaScript Frontend Frameworks. This is the contemporary evolutionary phase that we are in right now.

The common pattern amongst all the framework approaches discussed until now is that the server generates the ultimate HTML page that is displayed by the web browser. This, while being quite effective, does not maximize the potential that the client computer possesses. For instance, the entire process of building the UI and managing it (the <i>view</i> in MVC) can be offloaded to the browser such that the server only has to deal with the model & controller aspects (M & C). And in certain cases, even portions of the controller logic can be offloaded to the client browser.

It is this paradigm that has resulted in JavaScript based frontend frameworks such as [Angular](https://angular.io/), [React](https://react.dev/) & [Vue.js](https://vuejs.org/), amongst others.

JavaScript based frontend frameworks render the entire HTML page locally at the browser. They do this by running JavaScript code, which is served by the server. In these frameworks, the HTTP server is responsible for primarily two functions:

- Provide access to the data & manipulate them through a well defined interface
- Deliver the latest application code as JavaScript bundles

The JavaScript bundles run in the browser fetching essential data from the server and building an HTML user interface for the user. This HTML is then injected into the browser window resulting in the application UI and allows the user to interact with the app. When user invokes an application feature or triggers an action (like clicking a button or a link or entering a value into a text field), the relevant code goes on to build a new interface (or modifies the existing UI) by composing new HTML fragments and injecting them into the browser's view. This process goes on endlessly until the user quits the app.

This mechanism completely removes the logic of building the HTML response for a given request from the server. Server only has to provide a means to access the data & in cases where the data needs to be changed, a mechanism for it. Of course the server also incorporates the validation & business logic (such as cascading effects on other related data) of what happens data is thus modified. This is typically accomplished via a standard set of HTTP requests, with each type of request delegated to a specific role vis-a-vis the data it works on. This is typically referred to as the [REST](https://en.wikipedia.org/wiki/REST) API. (Rest stands for REpresentational State Transfer).

## Conclusion
I hope this article gave you an insight into way the web has evolved to result in what we have today. This is by no means complete and overlooks a key trend -- mechanisms for live interaction via browser. By mechanism for live interaction, I'm referring to features such as live chat and streaming. Both these features require data to be pushed by the server to the client, after the client initiates a request expressing interest in the data. If time permits, we will explore this in a little bit more detail in one of the future articles.

Also, how would two other key recent technological innovations that are vogue now(AI & VR) affect the web? Like in biology, it is too risky to make predictions on evolution. A smarter approach would be to sit, watch and adapt with it.