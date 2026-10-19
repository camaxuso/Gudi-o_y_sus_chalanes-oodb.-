<?php
const ROLES_VALIDOS = ['client', 'employee'];
const SEDES_VALIDAS = ['OTAY', 'FUNDADORES', 'PLAYAS'];

function cleanText(array $body, string $field, bool $required, int $max, array &$errors): ?string
{
    $value = $body[$field] ?? null;

    if ($value !== null && !is_scalar($value)) {
        $errors[] = "$field tiene un formato inválido";
        return null;
    }

    $value = $value === null ? '' : trim((string)$value);

    if ($value === '') {
        if ($required) {
            $errors[] = "$field es obligatorio";
        }
        return null;
    }

    if (mb_strlen($value) > $max) {
        $errors[] = "$field no puede tener más de $max caracteres";
        return null;
    }

    return $value;
}

function validateUserGym($body): array
{
    if (!is_array($body)) {
        return [null, ['El cuerpo de la petición debe ser un JSON válido']];
    }

    $errors = [];
    $clean  = [];

    $clean['name']      = cleanText($body, 'name', true, 50, $errors);
    $clean['LastnameP'] = cleanText($body, 'LastnameP', true, 50, $errors);
    $clean['LastnameM'] = cleanText($body, 'LastnameM', false, 50, $errors);

    $phone = cleanText($body, 'phonenum', false, 15, $errors);
    if ($phone !== null && !preg_match('/^\d{7,15}$/', $phone)) {
        $errors[] = 'phonenum debe contener solo dígitos (7 a 15)';
    }
    $clean['phonenum'] = $phone;

    $email = cleanText($body, 'email', false, 100, $errors);
    if ($email !== null && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = 'email no tiene un formato válido';
    }
    $clean['email'] = $email;

    $role = cleanText($body, 'role_gym', true, 20, $errors);
    if ($role !== null && !in_array($role, ROLES_VALIDOS, true)) {
        $errors[] = 'role_gym debe ser: ' . implode(', ', ROLES_VALIDOS);
    }
    $clean['role_gym'] = $role;

    $location = cleanText($body, 'location', true, 20, $errors);
    if ($location !== null && !in_array($location, SEDES_VALIDAS, true)) {
        $errors[] = 'location debe ser: ' . implode(', ', SEDES_VALIDAS);
    }
    $clean['location'] = $location;

    return [$clean, $errors];
}

function mapDbError(PDOException $ex): array
{
    $code = (int)($ex->errorInfo[1] ?? 0);

    switch ($code) {
        case 1062: 
            return [409, 'Ya existe un usuario con ese email'];
        case 1264:
            return [400, 'Un valor numérico está fuera de rango (revisa phonenum)'];
        case 1451: 
            return [409, 'No se puede eliminar: el usuario tiene registros relacionados (pagos, reportes, tarjetas, etc.)'];
        default:
            error_log($ex->getMessage()); 
            return [500, 'Error interno del servidor'];
    }
}
?>
