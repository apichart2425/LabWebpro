from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from .models import Profile,Poll,Question, Choice


def validate_even(value):
    if value % 2 != 0:
        raise ValidationError('%(value)s ไม่ใช่เลขคู่', params={'value': value})

class PollForm(forms.Form):
    title = forms.CharField(label="ชื่อโพล", max_length=100, required=True)
    email = forms.CharField(validators=[validators.validate_email])
    no_questions = forms.IntegerField(label="จำนวนคำถาม", min_value=0,
                                      max_value=10,
                                      required=True,
                                      validators=[validate_even])
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def clean_title(self):
        data = self.cleaned_data['title']

        if "ไอทีหมีแพนด้า" not in data:
            raise forms.ValidationError("TEST")

        return  data

    def clean(self):
        clean_data = super().clean()
        start = clean_data.get('start_date')
        end = clean_data.get('end_date')

        if start and not end:
            # raise forms.ValidationError('โปรดเลือกวันที่สิ้นสุด')
            self.add_error('end_date', 'โปรดเลือกวันที่สิ้นสุด')
        if end and not start:
            # raise forms.ValidationError('โปรดเลือกวันที่เริ่มต้น')
            self.add_error('start_date', 'โปรดเลือกวันที่สิ้นสุด')


class CommentForm(forms.Form):
    title = forms.CharField(max_length=100)
    body = forms.CharField(max_length=500, widget=forms.Textarea)
    email = forms.EmailField(required=False,)
    tel = forms.CharField(max_length=10,required=False)

    # def claen_tel(self):
    #     data = self.cleaned_data['tel']
    #     if len(data) != 10:
    #         raise forms.ValidationError('not 10 num')

    def clean(self):
        clean_data = super().clean()
        tel = clean_data.get('tel')
        email = clean_data.get('email')


        if not email and not tel:
            raise forms.ValidationError('ต้องกรอก email Mobile Number')

        if tel:
            if not tel.isdigit():
                self.add_error('tel','หมายเลขโทรศัพท์ต้องเป็นตัวเลขเท่านั้น')
            if len(tel) != 10:
                self.add_error('tel', 'หมายเลขโทรศัพท์ต้องมี10หลัก')

        if email and tel:
            raise forms.ValidationError('ต้องกรอก email Mobile Number')

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=100)
    new_password = forms.CharField(max_length=100)
    renew_password = forms.CharField(max_length=100)

    def clean(self):
        clean_data = super().clean()
        new_password = clean_data.get('new_password')
        renew_password = clean_data.get('renew_password')

        if new_password != renew_password:
             self.add_error('renew_password','รหัสผ่านใหม่ กับ ยืนยันรหัสผ่าน ต้องเหมือนกัน')

        if len(new_password) < 8 or len(renew_password) < 8 :
             self.add_error('renew_password','รหัสผ่านต้องมีตัวอักษรมากกว่า 8 ตัวอักษร')
        # or (len(new_password) > 8 and len(renew_password) > 8):


class RegisterForm(forms.Form):
    CHOICES =  Profile.GENDERS

    email = forms.EmailField(label="อีเมล์:")
    username = forms.CharField(max_length=100, label="ชื่อผู้ใช้:")
    password = forms.CharField(max_length=100, label="รหัสผ่าน:")
    re_password = forms.CharField(max_length=100,label="ยืนยันรหัสผ่าน:")
    line_id = forms.CharField(max_length=100,label="Line ID:", required=False)
    facebook =  forms.CharField(max_length=100,label="Facebook" , required=False)
    gender =  forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label="เพศ")
    birthdate = forms.DateField( label="วันเกิด:" , required=False)


    def clean(self):
        clean_data = super().clean()
        password = clean_data.get('password')
        re_password = clean_data.get('re_password')

        if password != re_password:
             self.add_error('re_password','รหัสผ่านใหม่ กับ ยืนยันรหัสผ่าน ต้องเหมือนกัน')

        if len(password) < 8 or len(re_password) < 8 :
             self.add_error('re_password','รหัสผ่านต้องมีตัวอักษรมากกว่า 8 ตัวอักษร')


class QuestionForm(forms.Form):
    question_id = forms.IntegerField(required = False, widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea)
    type = forms.ChoiceField(choices=Question.TYPES, initial='01')

class PollModelForm(forms.ModelForm):

    class Meta:
        model = Poll
        exclude = ['del_flag']

    def clean_title(self):
        data = self.cleaned_data['title']

        # if "ไอทีหมีแพนด้า" not in data:
        #     raise forms.ValidationError("TEST")

        return  data

    def clean(self):
        clean_data = super().clean()
        start = clean_data.get('start_date')
        end = clean_data.get('end_date')

        if start and not end:
            # raise forms.ValidationError('โปรดเลือกวันที่สิ้นสุด')
            self.add_error('end_date', 'โปรดเลือกวันที่สิ้นสุด')
        if end and not start:
            # raise forms.ValidationError('โปรดเลือกวันที่เริ่มต้น')
            self.add_error('start_date', 'โปรดเลือกวันที่สิ้นสุด')

class ChoiceModelForm(forms.ModelForm):
    class Meta:
        medel = Choice
        fields = '__all__'