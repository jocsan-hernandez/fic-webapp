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

    departamento = forms.ChoiceField(
        choices=[
            ("Atlántida", "Atlántida"),
            ("Choluteca", "Choluteca"),
            ("Colón", "Colón"),
            ("Comayagua", "Comayagua"),
            ("Copán", "Copán"),
            ("Cortés", "Cortés"),
            ("El Paraíso", "El Paraíso"),
            ("Francisco Morazán", "Francisco Morazán"),
            ("Gracias a Dios", "Gracias a Dios"),
            ("Islas de la Bahía", "Islas de la Bahía"),
            ("Intibucá", "Intibucá"),
            ("Lempira", "Lempira"),
            ("La Paz", "La Paz"),
            ("Ocotepeque", "Ocotepeque"),
            ("Olancho", "Olancho"),
            ("Santa Bárbara", "Santa Bárbara"),
            ("Valle", "Valle"),
            ("Yoro", "Yoro"),
        ]
    )

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

    departamento = forms.ChoiceField(
        choices=[
            ("Atlántida", "Atlántida"),
            ("Choluteca", "Choluteca"),
            ("Colón", "Colón"),
            ("Comayagua", "Comayagua"),
            ("Copán", "Copán"),
            ("Cortés", "Cortés"),
            ("El Paraíso", "El Paraíso"),
            ("Francisco Morazán", "Francisco Morazán"),
            ("Gracias a Dios", "Gracias a Dios"),
            ("Islas de la Bahía", "Islas de la Bahía"),
            ("Intibucá", "Intibucá"),
            ("Lempira", "Lempira"),
            ("La Paz", "La Paz"),
            ("Ocotepeque", "Ocotepeque"),
            ("Olancho", "Olancho"),
            ("Santa Bárbara", "Santa Bárbara"),
            ("Valle", "Valle"),
            ("Yoro", "Yoro"),
        ]
    )

    #Validaciones
    def clean(self):
        cleaned_data= super().clean()
        telefono = cleaned_data.get("telefono")
        if telefono and not telefono.isdigit():
            self.add_error("telefono", "El teléfono debería tener sólo números.")
        return cleaned_data    
    
class JoinRequestForm(forms.Form):
    nombreCompleto = forms.CharField(max_length=200, label="Nombre completo")

    telefono = forms.CharField(max_length=15, label="Número de télefono")

    def clean(self):
        cleaned_data= super().clean()
        telefono = cleaned_data.get("telefono")
        if telefono and not telefono.isdigit():
            self.add_error("telefono", "El teléfono debería tener sólo números.")
        return cleaned_data    
