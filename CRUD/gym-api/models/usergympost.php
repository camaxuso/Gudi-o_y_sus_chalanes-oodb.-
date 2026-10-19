<?php
$data         = null;
$errorMessage = null;
$statusCode   = 201;

[$clean, $errors] = validateUserGym($body);

if (!empty($errors)) {
    $statusCode   = 400;
    $errorMessage = implode('; ', $errors);
} else {
    try {
        $SQL_Query = 'INSERT INTO usergym (
            name,
            LastnameP,
            LastnameM,
            phonenum,
            email,
            role_gym,
            location
        ) VALUES (
            :name,
            :LastnameP,
            :LastnameM,
            :phonenum,
            :email,
            :role_gym,
            :location)';

        $SQL_Sentence = $DB_Connector->prepare($SQL_Query);
        $SQL_Sentence->execute([
            ':name'      => $clean['name'],
            ':LastnameP' => $clean['LastnameP'],
            ':LastnameM' => $clean['LastnameM'],   
            ':phonenum'  => $clean['phonenum'],
            ':email'     => $clean['email'],
            ':role_gym'  => $clean['role_gym'],
            ':location'  => $clean['location']
        ]);

        $newId = (int)$DB_Connector->lastInsertId();

        $SQL_Select = $DB_Connector->prepare('SELECT * FROM usergym WHERE id_user = :id_user');
        $SQL_Select->execute([':id_user' => $newId]);
        $data = $SQL_Select->fetch(PDO::FETCH_ASSOC);
    } catch (PDOException $ex) {
        [$statusCode, $errorMessage] = mapDbError($ex);
        $data = null;
    }
}
?>
