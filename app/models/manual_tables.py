# coding: utf-8

# Imports
from app.classes.MFEuroField import Class as MFEuroField
from django.db import models

class TProgrammeDetaillePrg(models.Model):

	# Colonnes

	prg_id = models.IntegerField(primary_key=True, verbose_name='ID')

	prg_mnt1 = MFEuroField(
		blank=True,
		null=True,
		verbose_name='Programme d\'actions - Montant contractualisé (en €)'
	)

	prg_mnt2 = MFEuroField(blank=True, null=True)

	prg_mnt3 = MFEuroField(blank=True, null=True)

	prg_mnt_est_ttc = models.BooleanField(
		verbose_name='Programme d\'actions - Le montant est-il TTC ?'
	)

	prg_nbre_dos = models.IntegerField(
		blank=True,
		null=True,
		verbose_name='Programme d\'actions - Nombre de dossiers contractualisés'
	)

	act_id = models.CharField(
		max_length=255, verbose_name='Axe/action d\'un programme d\'actions'
	)

	moa_id = models.ForeignKey(
		'TOrganisme',
		blank=True,
		db_column='moa_id',
		null=True,
		on_delete=models.DO_NOTHING,
		verbose_name='Maître d\'ouvrage'
	)

	prg_mnt_contrac_autres = MFEuroField(
		blank=True,
		null=True,
		verbose_name='Autres - Montant contractualisé (en €)'
	)

	prg_mnt_comman_autres = MFEuroField(
		blank=True,
		null=True,
		verbose_name='Autres - Montant commandé (en €)'
	)

	prg_mnt_factu_autres = MFEuroField(
		blank=True,
		null=True,
		verbose_name='Autres - Montant facturé (en €)'
	)

	class Meta:
		db_table = '"hors_public"."t_programme_detaille_prg"'
		managed = False
		verbose_name = 'Détail des axes et actions d\'un programme d\'actions'
		verbose_name_plural = 'Détail des axes et actions d\'un programme d\'actions'

	# Méthodes

	def get_pro(self):

		"""
		Programme
		"""

		# Imports
		from app.models import TProgramme

		return TProgramme.objects.get(pk=self.act_id.split('_')[0])

	def get_brn(self):

		"""
		Axe, sous-axe ou action
		"""

		# Imports
		from app.models import TAction
		from app.models import TAxe
		from app.models import TSousAxe

		act_id_splitted = self.act_id.split('_')[1:]
		act_id_splitted_len = len(act_id_splitted)

		if act_id_splitted_len == 1:
			return TAxe.objects.get(pk=self.act_id)
		if act_id_splitted_len == 2:
			return TSousAxe.objects.get(pk=self.act_id)
		else:
			return TAction.objects.get(pk=self.act_id)

	# Méthodes Django

	def __str__(self):
		return ' - '.join([
			str(i) for i in [self.get_pro(), self.get_brn(), self.moa_id
		] if i])