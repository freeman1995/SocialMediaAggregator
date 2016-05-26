<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Social Media Aggregator</title>
</head>
<body>
    <h1>Social Media Aggregator</h1>

    </br>
    </br>

    <form action="/load_page" method="post">
        Page URL or Slug or ID: <input name="page_url" type="text" />
        <input value="Load!" type="submit" />
    </form>

    </br>
    </br>

    %for page in page_list:
        <li>
        <img src="{{page['picture']}}"></br>
        {{page['name']}}</br>
        About: {{page['about']}}</br>
        {{page['fan_count']}} fans.</br>
        <a href="/posts/{{page['fbid']}}/{{page['name']}}"> View posts </a></br>
        <a href="{{page['link']}}"> View page in Facebook </a></br>
        <a href="/remove_page/{{page['fbid']}}"> Remove page </a></br>
        </br>
        </br>
    </li>
</body>
</html>