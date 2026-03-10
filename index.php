<?php
$data = null;
$error = null;

if(isset($_POST['url'])){

$url = filter_var($_POST['url'], FILTER_VALIDATE_URL);

if($url){

$escaped = escapeshellarg($url);

$json = shell_exec("python3 seo_analyzer.py $escaped");

$data = json_decode($json,true);

}else{

$error = "Invalid URL";

}

}
?>

<!DOCTYPE html>
<html>
<head>

<title>SEO Analyzer</title>

<style>

body{
font-family: Arial;
background:#f4f6f8;
margin:0;
padding:40px;
}

.container{
max-width:1000px;
margin:auto;
}

h1{
text-align:center;
}

form{
display:flex;
gap:10px;
margin-bottom:30px;
}

input{
flex:1;
padding:12px;
font-size:16px;
}

button{
padding:12px 20px;
background:#4CAF50;
color:white;
border:none;
cursor:pointer;
}

.card{
background:white;
padding:20px;
margin-bottom:20px;
border-radius:8px;
box-shadow:0 2px 8px rgba(0,0,0,0.1);
}

.grid{
display:grid;
grid-template-columns:1fr 1fr;
gap:20px;
}

.score{
font-size:48px;
font-weight:bold;
color:#4CAF50;
}

.bad{
color:red;
}

.keyword{
display:inline-block;
background:#eee;
padding:6px 10px;
margin:5px;
border-radius:6px;
}

</style>

</head>

<body>

<div class="container">

<h1>SEO Analyzer</h1>

<form method="POST">
<input type="text" name="url" placeholder="https://example.com" required>
<button>Analyze</button>
</form>

<?php if($error){ ?>
<div class="card bad"><?php echo $error; ?></div>
<?php } ?>

<?php if($data && !isset($data['error'])){ ?>

<div class="card">

<h2>SEO Score</h2>

<div class="score">
<?php echo $data['seo_score']; ?>/100
</div>

</div>

<div class="grid">

<div class="card">

<h3>Basic Info</h3>

<p><b>URL:</b> <?php echo htmlspecialchars($data['url']); ?></p>
<p><b>Domain:</b> <?php echo htmlspecialchars($data['domain']); ?></p>
<p><b>Server IP:</b> <?php echo htmlspecialchars($data['ip_address']); ?></p>
<p><b>HTTPS:</b> <?php echo $data['https'] ? "Yes" : "No"; ?></p>
<p><b>Load Time:</b> <?php echo $data['load_time']; ?> s</p>
<p><b>Page Size:</b> <?php echo $data['page_size_kb']; ?> KB</p>
<p><b>Word Count:</b> <?php echo $data['word_count']; ?></p>
<p><b>Mobile Friendly:</b> <?php echo $data['mobile_friendly'] ? "Yes" : "No"; ?></p>

</div>

<div class="card">

<h3>Meta Data</h3>

<p><b>Title:</b> <?php echo htmlspecialchars($data['title']); ?></p>
<p><b>Title Length:</b> <?php echo $data['title_length']; ?></p>
<p><b>Description:</b> <?php echo htmlspecialchars($data['description']); ?></p>
<p><b>Canonical:</b> <?php echo htmlspecialchars($data['canonical']); ?></p>
<p><b>Robots Meta:</b> <?php echo htmlspecialchars($data['robots_meta']); ?></p>

</div>

</div>

<div class="grid">

<div class="card">

<h3>Structure</h3>

<p><b>H1:</b> <?php echo $data['h1_count']; ?></p>
<p><b>H2:</b> <?php echo $data['h2_count']; ?></p>
<p><b>Schema.org:</b> <?php echo $data['schema_count']; ?></p>

</div>

<div class="card">

<h3>Links</h3>

<p><b>Internal:</b> <?php echo $data['internal_links']; ?></p>
<p><b>External:</b> <?php echo $data['external_links']; ?></p>

</div>

</div>

<div class="grid">

<div class="card">

<h3>Technical SEO</h3>

<p><b>Robots.txt:</b> <?php echo $data['robots_txt'] ? "Found" : "Missing"; ?></p>
<p><b>Sitemap:</b> <?php echo $data['sitemap'] ? "Found" : "Missing"; ?></p>
<p><b>Favicon:</b> <?php echo htmlspecialchars($data['favicon']); ?></p>

</div>

<div class="card">

<h3>Social SEO</h3>

<p><b>OpenGraph Title:</b> <?php echo htmlspecialchars($data['og_title']); ?></p>
<p><b>OpenGraph Description:</b> <?php echo htmlspecialchars($data['og_description']); ?></p>
<p><b>OpenGraph Image:</b> <?php echo htmlspecialchars($data['og_image']); ?></p>
<p><b>Twitter Card:</b> <?php echo htmlspecialchars($data['twitter_card']); ?></p>

</div>

</div>

<div class="card">

<h3>Images Missing ALT</h3>

<?php

if(count($data['images_missing_alt']) == 0){

echo "<p>All images have ALT tags 🎉</p>";

}else{

foreach($data['images_missing_alt'] as $img){

echo "<p class='bad'>⚠ URL: ".htmlspecialchars($img['url'])." | Suggested ALT: ".htmlspecialchars($img['suggested_alt'])."</p>";

}

}

?>

</div>

<div class="card">

<h3>Top Keywords</h3>

<?php

foreach($data['top_keywords'] as $k){

echo "<span class='keyword'>".$k[0]." (".$k[1].")</span>";

}

?>

</div>

<div class="card">

<h3>SEO Issues</h3>

<?php

if(count($data['issues'])==0){

echo "<p>No major issues detected 🎉</p>";

}else{

foreach($data['issues'] as $issue){

echo "<p class='bad'>⚠ ".htmlspecialchars($issue['issue'])."</p>";

if(isset($issue['suggestion'])){

echo "<p>💡 ".htmlspecialchars($issue['suggestion'])."</p>";
}
}

}

?>

</div>

<?php } ?>

</div>

</body>
</html>