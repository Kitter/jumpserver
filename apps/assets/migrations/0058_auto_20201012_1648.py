# Generated by Django 2.2.13 on 2020-10-12 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0057_fill_node_value_assets_amount_and_parent_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemuser',
            name='protocol',
            field=models.CharField(choices=[('ssh', 'ssh'), ('rdp', 'rdp'), ('telnet', 'telnet'), ('vnc', 'vnc'), ('mysql', 'mysql'), ('oracle', 'oracle'), ('mariadb', 'mariadb'), ('postgresql', 'PostgreSQL'), ('k8s', 'k8s')], default='ssh', max_length=16, verbose_name='Protocol'),
        ),
    ]