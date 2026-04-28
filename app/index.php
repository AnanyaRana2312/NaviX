<?php 
// Get environment variables 
$db_host = getenv('DB_HOST') ?: 'db'; 
$db_user = getenv('DB_USER') ?: 'root'; 
$db_pass = getenv('DB_PASSWORD') ?: 'example'; 
$db_name = getenv('DB_NAME') ?: 'myapp'; 
 
echo "<h1>Docker Assignment</h1>"; 
echo "&lt;h3&gt;Environment Variables:&lt;/h3&gt;"; 
echo "DB_HOST: " . $db_host . "&lt;br&gt;"; 
echo "DB_USER: " . $db_user . "&lt;br&gt;"; 
echo "DB_NAME: " . $db_name . "&lt;br&gt;&lt;br&gt;"; 
 
// Try to connect to database 
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name); 
if ($conn- { 
    echo "&lt;p style='color:red'&gt;Database Connection Failed: " . $conn- . "&lt;/p&gt;"; 
} else { 
    echo "&lt;p style='color:green'&gt;û Database Connected Successfully!&lt;/p&gt;"; 
    $conn-
} 
?> 
