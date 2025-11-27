
document.getElementById('rut').addEventListener('input', function (e) {
    let raw = e.target.value
        .replace(/\./g, '')       // Quita los puntos
        .replace(/-/g, '')        // Quita el guion
        .replace(/[^0-9kK]/g, '') // Solo permite dígitos y K/k
        .toUpperCase();           // Convierte la K en mayúscula

    // Verifica si la longitud del RUT limpio es mayor a 1 (lo que permite separar el cuerpo del dígito verificador)
    if (raw.length > 1) {
        let cuerpo = raw.slice(0, -1);
        // Separa el digito verificador
        let dv = raw.slice(-1);
        // Formatea el contenido del RUT: inserta puntos cada tres dígitos, contando desde la derecha
        cuerpo = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        // Asigna el valor final formateado al campo de entrada
        e.target.value = `${cuerpo}-${dv}`;
    } else {
        // Si solo hay 0 o 1 carácter, simplemente mantiene el valor limpio (sin formato)
        e.target.value = raw;
    }
});

// Funcion Mostrar/Ocultar Contraseña
document.getElementById('togglePassword').addEventListener('click', function () {
    // Obtiene el elemento de entrada de la contraseña por su ID.
    const passwordInput = document.getElementById('password');
    // Determina si el campo de entrada está oculto (type es 'password').
    const isHidden = passwordInput.type === 'password';
    // Alterna el atributo 'type' del campo de entrada:
    // Si estaba oculto ('password'), lo cambia a 'text'
    // Si estaba visible ('text'), lo cambia a 'password'
    passwordInput.type = isHidden ? 'text' : 'password';
});