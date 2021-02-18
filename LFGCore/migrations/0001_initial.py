# Generated by Django 3.1.5 on 2021-02-16 22:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address1', models.CharField(max_length=45)),
                ('address2', models.CharField(max_length=45)),
                ('apartment_number', models.CharField(max_length=45)),
                ('city', models.CharField(max_length=45)),
                ('state', models.CharField(max_length=45)),
                ('zipcode', models.CharField(max_length=45)),
                ('country', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=2000)),
                ('time_sent', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChatChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_type', models.CharField(choices=[('D', 'Direct'), ('P', 'Project')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_status', models.CharField(choices=[('RQ', 'Requested'), ('AC', 'Accepted'), ('RJ', 'Rejected')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_owner', models.BooleanField()),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=10000)),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=250)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.skill')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=45)),
                ('description', models.CharField(max_length=1000)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.project')),
                ('skills', models.ManyToManyField(to='LFGCore.Skill')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.chatchannel')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.project')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='channels',
            field=models.ManyToManyField(through='LFGCore.ProjectChannel', to='LFGCore.ChatChannel'),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.CharField(max_length=1000)),
                ('telephone_number', models.DecimalField(decimal_places=0, max_digits=11)),
                ('address', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.address')),
                ('chat_channels', models.ManyToManyField(related_name='channels', to='LFGCore.ChatChannel')),
                ('chats', models.ManyToManyField(related_name='chats', through='LFGCore.Chat', to='LFGCore.ChatChannel')),
                ('friends', models.ManyToManyField(related_name='_profile_friends_+', through='LFGCore.Friend', to='LFGCore.Profile')),
                ('projects', models.ManyToManyField(through='LFGCore.Member', to='LFGCore.Project')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.project'),
        ),
        migrations.AddField(
            model_name='member',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.role'),
        ),
        migrations.AddField(
            model_name='member',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.profile'),
        ),
        migrations.AddField(
            model_name='friend',
            name='reciever',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reciever', to='LFGCore.profile'),
        ),
        migrations.AddField(
            model_name='friend',
            name='requestor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requestor', to='LFGCore.profile'),
        ),
        migrations.AddField(
            model_name='chat',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LFGCore.chatchannel'),
        ),
        migrations.AddField(
            model_name='chat',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_user', to='LFGCore.profile'),
        ),
    ]