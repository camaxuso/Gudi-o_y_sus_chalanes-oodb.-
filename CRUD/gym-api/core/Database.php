<?php
try {
    $DB_Connector = new PDO(
        'mysql:host=localhost;port=3307;dbname=gym',
        'root',
        '1234'
    );
    $DB_Connector->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $DB_Connector->exec("SET CHARACTER SET utf8mb4");
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'data' => null,
        'message' => 'Database connection failed'
    ]);
    exit;
}
?>