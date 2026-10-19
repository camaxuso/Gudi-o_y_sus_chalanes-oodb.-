<?php
$data         = [];
$errorMessage = null;
$statusCode   = 200;

try {
    if ($id !== null) {
        $SQL_Sentence = $DB_Connector->prepare('SELECT * FROM usergym WHERE id_user = :id_user');
        $SQL_Sentence->execute([':id_user' => $id]);
        $row = $SQL_Sentence->fetch(PDO::FETCH_ASSOC);

        if ($row === false) {
            $statusCode   = 404;
            $errorMessage = 'Usuario no encontrado';
            $data         = null;
        } else {
            $data = $row;
        }
    } else {
        $SQL_Sentence = $DB_Connector->prepare('SELECT * FROM usergym ORDER BY id_user');
        $SQL_Sentence->execute();
        $data = $SQL_Sentence->fetchAll(PDO::FETCH_ASSOC);
    }
} catch (PDOException $ex) {
    [$statusCode, $errorMessage] = mapDbError($ex);
    $data = null;
}
?>
