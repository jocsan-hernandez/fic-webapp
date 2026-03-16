from django import forms

#Formulario de registro
class UserRegisterForm(forms.Form):
    nombreCompleto= forms.CharField(max_length=200, label="Nombre completo")
    
    identidad= forms.CharField(max_length=20, label="No. identidad")

    tipoUsuario = forms.ChoiceField(
        choices=[
            ("cliente", "Cliente"),
            ("admin", "Administrador")
        ], label="Tipo de Usuario"
    )

    correo= forms.EmailField(label="Correo electrónico")

    cuentaBanco= forms.CharField(max_length=50, required=False, label="Cuenta de banco")

    nombreBanco= forms.CharField(max_length=100, required=False, label="Nombre del banco")

    telefono= forms.CharField(max_length=15, label="Número de télefono")

    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    confirmPassword = forms.CharField(widget=forms.PasswordInput, label = "Confirme contraseña")

    #Validaciones
    def clean(self):
        cleaned_data= super().clean()

        password = cleaned_data.get("password")

        confirm = cleaned_data.get("confirmPassword")

        if password != confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data
    

#Formulario de login
class UserLoginForm(forms.Form):
    correo= forms.EmailField(
        label="Correo electrónico"
    )    

    password = forms.CharField(
        widget= forms.PasswordInput, label="Contraseña"
    )

    #Validaciones
    def clean(self):
        cleaned_data= super().clean()

        password= cleaned_data.get("password")
        correo = cleaned_data.get("correo")

        if not correo or not password:
            raise forms.ValidationError("Todos los campos son obligatorios")
        return cleaned_data
    
#Formulario para editar informacion
class UserUpdateForm(forms.Form):
    nombreCompleto= forms.CharField(max_length=200, label="Nombre completo")
    
    identidad= forms.CharField(max_length=20, label="No. identidad")

    tipoUsuario = forms.ChoiceField(
        choices=[
            ("cliente", "Cliente"),
            ("admin", "Administrador")
        ], label="Tipo de Usuario"
    )

    correo= forms.EmailField(label="Correo electrónico")

    cuentaBanco= forms.CharField(max_length=50, required=False, label="Cuenta de banco")

    nombreBanco= forms.CharField(max_length=100, required=False, label="Nombre del banco")

    telefono= forms.CharField(max_length=15, label="Número de télefono")

    #Validaciones
    def clean(self):
        cleaned_data= super().clean()
        telefono = cleaned_data.get("telefono")
        if telefono and not telefono.isdigit():
            self.add_error("telefono", "El teléfono debería tener sólo números.")
        return cleaned_data    
