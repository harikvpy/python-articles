# Evolution of Web Frameworks
<cite>Hariharan Mahadevan(何瑞理), hari@smallpearl.com</cite>

## What is a Web Frameowrk
Web framework is a software framework designed to support the development of web sites and applications. They provide a standard way to build and deploy web applications and provide software tools to automate the overhead associated with common activities performed in web development such as database access, user management, access control, session management, etc. The fundamental objective of a web framework is to promote code reuse by reducing repetitive tasks into a common set of reusable components.

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

Whether MVC or MVT or some other pattern, a common abstraction in all these patters is the separation of the model, view and the controller. Model refers to the actual data which is typically stored in a database. View is that is presented to the end user. Controller is the logic that translates the data retrieved from the database (or somewhere else) and provides it to the view.

Besides scalability, the advantage of these frameworks is the basic security that they guarantee. By forcing the application to fit within the framework, web applications inherit the minimum security guarantees that the framework offers. For instance, most of these frameworks, by default require production sites to be served over HTTPS. Also, operations that result in changes to the backend data require additional precautions (often provided by default by the framework) in the code all but eliminating risks posed by common low-cost attacks by hackers.

Heavier