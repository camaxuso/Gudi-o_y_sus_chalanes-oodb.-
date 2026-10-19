<?php
$data         = null;
$errorMessage = null;
$statusCode   = 200;

[$clean, $errors] = validateUserGym($body);

if (!empty($errors)) {
    $statusCode   = 400;
    $errorMessage = implode('; ', $errors);
} else {
    try {
       
        $SQL_Check = $DB_Connector->prepare('SELECT id_user FROM usergym WHERE id_user = :id_user');
        $SQL_Check->execute([':id_user' => $id]);

        if ($SQL_Check->fetch() === false) {
            $statusCode   = 404;
            $errorMessage = 'Usuario no encontrado';
        } else {
            $SQL_Query = 'UPDATE usergym SET
                name = :name,
                LastnameP = :LastnameP,
                LastnameM = :LastnameM,
                phonenum = :phonenum,
                email = :email,
                role_gym = :role_gym,
                location = :location
                WHERE
                id_user = :id_user';

            $SQL_Sentence = $DB_Connector->prepare($SQL_Query);
            $SQL_Sentence->execute([
                ':id_user'   => $id,
                ':name'      => $clean['name'],
                ':LastnameP' => $clean['LastnameP'],
                ':LastnameM' => $clean['LastnameM'],
                ':phonenum'  => $clean['phonenum'],
                ':email'     => $clean['email'],
                ':role_gym'  => $clean['role_gym'],
                ':location'  => $clean['location']
            ]);

            $SQL_Select = $DB_Connector->prepare('SELECT * FROM usergym WHERE id_user = :id_user');
            $SQL_Select->execute([':id_user' => $id]);
            $data = $SQL_Select->fetch(PDO::FETCH_ASSOC);
        }
    } catch (PDOException $ex) {
        [$statusCode, $errorMessage] = mapDbError($ex);
        $data = null;
    }
}
?>
