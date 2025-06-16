# Qless

## Inspiration
We were inspired by both Yelp and Tripadvisor. We noticed that results on both of these sites are often dominated by larger businesses and chains. QLess aims to provide an alternative that is more welcoming to small businesses while simultaneously providing an added level of convenience for customers by allowing them to pick a restaurant based on distance from a given location and wait times calculated by the restaurant itself.

## What it does
QLess provides small businesses with exposure, an essential element to the success of any business. Our website has two pages: one for customers and one for businesses. Businesses can claim their restaurant and provide information about wait times and the restaurant’s operation. This information is then shown to the customer when they search for nearby small businesses. Overall, QLess connects businesses to potential customers and helps improve the dining experience for customers.

## How we built it
We built QLess's backend using Flask, Python, and JavaScript , and we used HTML and CSS for the frontend. To obtain information for its various functions, QLess uses two APIs: Free Restaurant API for the list of restaurants and their information, and GeoPy for geolocation and distance calculations. We also use libraries, including Datetime and Requests.

## Challenges we ran into
We jumped into QLess with minimal knowledge of Flask and APIs. We ran into numerous bugs -- from ports that wouldn’t open to disappearing webpages. We even created a logistic regression model to try to identify small businesses, but we were forced to scrap it because of a lack of training data for the model to effectively identify businesses. Despite these challenges, we were able to work together to resolve our issues and create a functioning app.

## Accomplishments that we're proud of
We can all collectively say that this is one of the most complex and polished projects we have worked on. In the past 24 hours, we created a project that we wouldn’t have thought was possible the day before.

One of our proudest achievements is our use of APIs in our website. We cycled through over 5 APIs on QLess, thoroughly researching and testing every single one of them. In the end, we found two APIs (Free Restaurant API and GeoPy)that were able to provide us with all of the information we needed and more when combined. We ended up using 9 different Google accounts to create free API keys to get our app fully functional.

## What we learned
We walked in with the question, What can we create to help small businesses? Not only did we create a successful app that met our goal, but we also learned a lot along the way. For most of us, this was our first hackathon. We discovered just how much we can learn and accomplish in a short period.

This project taught us patience and discipline when things didn’t go as planned. We learned more about APIs, Flask, and web development.

## What's next for QLess
Our goal with QLess was to create a platform to connect small businesses to potential customers. We believe we accomplished this, but we want to keep going and take QLess to the next level by creating a QLess mobile app. With a mobile app and a website, QLess would be accessible by everyone, fueling the success of small businesses around the world.
