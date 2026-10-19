<?php
$data         = null;
$errorMessage = null;
$statusCode   = 200;

try {
    $SQL_Sentence = $DB_Connector->prepare('DELETE FROM usergym WHERE id_user = :id_user');
    $SQL_Sentence->execute([':id_user' => $id]);

    if ($SQL_Sentence->rowCount() === 0) {
        $statusCode   = 404;
        $errorMessage = 'Usuario no encontrado';
    } else {
        $data = ['id_user' => $id];
    }
} catch (PDOException $ex) {
    [$statusCode, $errorMessage] = mapDbError($ex);
    $data = null;
}
?>
