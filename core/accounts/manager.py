from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("has_approval", True)
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("role", "admin")

        if kwargs["is_staff"] is not True:
            raise ValueError("Admin must have is_staff=True.")
        
        if kwargs["is_superuser"] is not True:
            raise ValueError("Admin must have is_superuser=True.")
        
        return self.create_user(email, password, **kwargs)
    
    def create_moderator(self, email, password, **kwargs):
        kwargs.setdefault("has_approval", True)
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", False)
        kwargs.setdefault("role", "moderator")

        if kwargs["is_staff"] is not True:
            raise ValueError("Moderator must have is_staff=True.")
        
        if kwargs["is_superuser"] is not False:
            raise ValueError("Moderator cannot have is_superuser=True.")
        
        return self.create_user(email, password, **kwargs)
