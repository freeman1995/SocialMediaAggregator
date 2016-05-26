<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Social Media Aggregator</title>
</head>
<body>
    <h1>{{page_name}} posts</h1>

    </br>
    </br>

    %for post in post_list:
        <li>
            %if 'message' in post:
                {{post['message']}}</br>
            %if 'picture' in post:
                <img src="{{post['picture']}}"></br>
            %if 'link' in post:
                <a href="{{post['link']}}"> Source </a></br>
            <b>{{post['created_time']}}</b></br>
            <b>{{post['likes']}} likes</b></br>
            <a href="{{post['permalink_url']}}"> View post in Facebook </a></br>
            </br>
            </br>
        </li>
</body>
</html>