from wtforms import SelectField

# Function for non-validating select fields
class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass
