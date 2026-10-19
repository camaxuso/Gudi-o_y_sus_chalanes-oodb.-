<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$uri = rtrim(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH), '/');
if ($uri === '') {
    $uri = '/';
}

$body = json_decode(file_get_contents('php://input'), true);

function respond(int $status, $data, ?string $error = null, string $message = 'Todo bien'): void
{
    http_response_code($status);
    echo json_encode([
        'success' => $error === null,
        'data'    => $error === null ? $data : null,
        'message' => $error ?? $message
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

require_once("core/Database.php");          
require_once("models/usergymhelpers.php"); 

$id = null; 

if ($method === 'GET' && $uri === '/health-check') {

    respond(200, ['language' => 'php'], null, 'API online');

} elseif ($method === 'GET' && $uri === '/Users') {

    require_once("models/usergymselect.php");
    respond($statusCode, $data, $errorMessage);

} elseif ($method === 'GET' && preg_match('#^/Users/(\d+)$#', $uri, $m)) {

    $id = (int)$m[1];
    require_once("models/usergymselect.php");
    respond($statusCode, $data, $errorMessage);

} elseif ($method === 'POST' && $uri === '/post') {

    require_once("models/usergympost.php");
    respond($statusCode, $data, $errorMessage);

} elseif ($method === 'PUT' && preg_match('#^/put/(\d+)$#', $uri, $m)) {

    $id = (int)$m[1]; // el ID de la URL es el que manda
    require_once("models/usergymput.php");
    respond($statusCode, $data, $errorMessage);

} elseif ($method === 'DELETE' && preg_match('#^/delete/(\d+)$#', $uri, $m)) {

    $id = (int)$m[1];
    require_once("models/usergymdelete.php");
    respond($statusCode, $data, $errorMessage);

} else {

    respond(404, null, 'Not Found');

}
?>
