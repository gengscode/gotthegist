import httplib2, re
from bs4 import BeautifulSoup, SoupStrainer
import mechanize
import cookielib
import html2text
from pattern.web import URL
from urlparse import urlparse, urljoin
import os
import sys
import ntpath

print "---------------"
print "   "
print "Please enter your HBS login credentials..."
print "   "


def geng(value, deletechars):
	for c in deletechars:
		value = value.replace(c, '')
	return value



username = raw_input("HBS Email: ")
password = raw_input("Password: ")

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# so the website thinks I'm a real computer!
br.addheaders = [('User-agent', 'Chrome')]


# The site we will navigate into, handling it's session
br.open('https://lh.hbs.edu')


# Select the form
br.select_form(name="loginForm")

# User credentials
br.form['username'] = username
br.form['password'] = password

# Login
response = br.submit()

courses_urls = []
courses_texts = []

# find the links to the course pages
for link in BeautifulSoup(response).find_all('a', href= re.compile('^/d2l/lp/ouHome/home')):
	try:
		if link.contents not in courses_texts:
			courses_urls.append(('https://lh.hbs.edu'+link['href']))
			courses_texts.append((link.contents))
	# if there is an error, just pass...sometimes there are errors
	# or try 'except ValueError:'
	except:
		pass

#confirm that were were able to find the course links (i.e. that the list is not empty)
if not courses_urls:
	print "---------------"
	print "     "
	print "Sorry, we were unable to login with that username and password"
	print "please try running the program again"
	print "     "
	print "---------------"
	raise SystemExit
else:
	print "     "
	print "     "
	print "     "
	print "logged in successfully!"
	print "     "
	print "     "
	print "     "
	print "Commencing downloading..."
	print "     "
	print "     "
	print "     "	


syllabus_urls = []



# create a list of the syllabus pages for each course (based on each course's 5 digit code taken from the course's homepage URL)
for i in courses_urls:
	my_string= i
	syllabus_urls.append(('https://lh.hbs.edu/d2l/le/calendar/'+ my_string.split("=",1)[1]+ '/syllabus/SyllabusView'))

# create a list of each course's short name (e.g. 'DCO' instead of 'DCO: DESIGNING COMPETITIVE ORGANIZATIONS SECTION 01')
course_count = 0
for course in courses_texts:
	courses_texts[course_count][0] = courses_texts[course_count][0].split(":")[0]
	course_count+=1


course_number = 0



# scrape all the files on each syllabus page!
for syllabus in syllabus_urls:

	# open each syllabus page
	response = br.open(syllabus)


	#create a list of cases
	cases_urls = []
	cases_texts = []
	# print the links to screen only if they start with 'https://cb.', as that is what most the Cases links start with
	for link in BeautifulSoup(response).find_all('a', href= re.compile('^https://cb.')):
		if (' ' in link['href']) == True:
			new_link = link['href'].replace(' ', '%20')
			new_name = link.contents
#			new_name = geng(new_name, '\/:*?"<>|')
			new_name[0] = ntpath.basename(new_name[0])
			cases_urls.append(new_link)
			cases_texts.append(new_name)
		else:
			cases_urls.append(link['href'])
			cases_texts.append(link.contents)


	# for whatever reason, you can't use 'response' twice in Beautifulsoup, so I have to get all the info again
	# we are already logged in, so we can just br.open
	check = br.open(syllabus)

	#create a list of readings
	readings_urls = []
	readings_texts = []
	# print the links to screen only if they contain "content", as that is what the readings often start with
	for link in BeautifulSoup(check).find_all('a', href=re.compile('^/content/')):
		if (' ' in link['href']) == True:
			new_link = link['href'].replace(' ', '%20')
			new_name = link.contents
#			new_name = geng(new_name, '\/:*?"<>|')
			new_name[0] = ntpath.basename(new_name[0])
			if "case" in link.contents[0].lower():
				cases_urls.append(('https://lh.hbs.edu'+new_link.split("?")[0]))
				cases_texts.append(new_name)
			else:
				readings_urls.append(('https://lh.hbs.edu'+new_link.split("?")[0]))
				readings_texts.append(new_name)
		else:
			# but if it has the word "case", add it to the Case list
			if "case" in link.contents[0].lower():
				cases_urls.append(('https://lh.hbs.edu'+link['href'].split("?")[0]))
				cases_texts.append(link.contents)
			else:
				readings_urls.append(('https://lh.hbs.edu'+link['href'].split("?")[0]))
				readings_texts.append(link.contents)
	
	#open the syllabus again
	check = br.open(syllabus)

	# print the links to screen only if they contain "services", as that is what the readings often start with
	for link in BeautifulSoup(check).find_all('a', href=re.compile('^https://services')):
		if (' ' in link['href']) == True:
			new_link = link['href'].replace(' ', '%20')
			new_name = link.contents
#			new_name = geng(new_name, '\/:*?"<>|')
			new_name[0] = ntpath.basename(new_name[0])
			if "case" in link.contents[0].lower():
				cases_urls.append(new_link)
				cases_texts.append(new_name)
			else:
				readings_urls.append(new_link)
				readings_texts.append(new_name)
		else:
			# but if it has the word "case", add it to the Case list
			if "case" in link.contents[0].lower():
				cases_urls.append(link['href'])
				cases_texts.append(link.contents)
			else:
				readings_urls.append(link['href'])
				readings_texts.append(link.contents)

	#create folders for each course
	if not os.path.exists(courses_texts[course_number][0]):
	    os.makedirs(courses_texts[course_number][0])
	#create subfolders for "cases"
	if not os.path.exists(courses_texts[course_number][0]+'/cases'):
	    os.makedirs(courses_texts[course_number][0]+'/cases')
	#create subfolders for "readings"
	if not os.path.exists(courses_texts[course_number][0]+'/readings'):
	    os.makedirs(courses_texts[course_number][0]+'/readings')




	case_number = 0;
	# write the case pdfs!
	for i in cases_urls:
		# Browser
		br = mechanize.Browser()

		# Cookie Jar - use the cookie that was set from before
		br.set_cookiejar(cj)

		# Browser options
		br.set_handle_equiv(True)
		br.set_handle_gzip(True)
		br.set_handle_redirect(True)
		br.set_handle_referer(True)
		br.set_handle_robots(False)
		br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

		br.addheaders = [('User-agent', 'Chrome')]
		output = br.open(i)
		# maybe put in something that says if response.code == '200', then execute the rest...
		url = URL(i)
		f = open(os.path.join(courses_texts[course_number][0]+'/cases', cases_texts[case_number][0]+'.pdf'), 'wb')
	# remember the timeout parameter, or else it will automatically timeout before you are done downloading	
		f.write(output.read())
		f.close()
		print "downloading... " + courses_texts[course_number][0] + "- " + cases_texts[case_number][0]
		case_number+=1




	# write the readings pdfs!
	reading_number = 0;
	for i in readings_urls:
		# Browser
		br = mechanize.Browser()

		# Cookie Jar - use the cookie that was set from before
		br.set_cookiejar(cj)

		# Browser options
		br.set_handle_equiv(True)
		br.set_handle_gzip(True)
		br.set_handle_redirect(True)
		br.set_handle_referer(True)
		br.set_handle_robots(False)
		br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

		br.addheaders = [('User-agent', 'Chrome')]

		output = br.open(i)

		# find out the file type and append it to the end of the file name
		if i[-4] == '.':
			#url = URL(i)
			f = open(os.path.join(courses_texts[course_number][0]+'/readings', readings_texts[reading_number][0]+i[-4:]), 'wb')
		elif i[-5] == '.':
			f = open(os.path.join(courses_texts[course_number][0]+'/readings', readings_texts[reading_number][0]+i[-5:]), 'wb')		
		else:
			f = open(os.path.join(courses_texts[course_number][0]+'/readings', readings_texts[reading_number][0]+'.pdf'), 'wb')

		# remember the timeout parameter, or else it will automatically timeout before you are done downloading	
		f.write(output.read())
		#f.write(url.download(timeout=150, cached=False))
		f.close()
		print "downloading... " + courses_texts[course_number][0] + "- " + readings_texts[reading_number][0]
		reading_number+=1

	#show progress in the terminal window
	print courses_texts[course_number][0] + " complete!"
	course_number += 1


# boom!  done
print "complete!"
