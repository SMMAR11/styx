# from app.functions import gen_cdc
from app.models import TAxe
from app.models import TSousAxe
from app.models import TMoa
from app.models import TProgramme
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from django.db import connections
# from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
# import csv

decorators = [csrf_exempt, login_required(login_url='index')]


@method_decorator(decorators, name='dispatch')
class AvancementProgrammeView(View):
    """Affichage du formulaire de réalisation d'un état "avancement de programme"
    Affiche les donnée de la vue postgres v_progs_detailles_complet
    Permet le filtre de ces données
    Permet l'export csv
    """

    template_name = 'realisation_etats/avancement_programme.html'

    def list_fetch_all(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [OrderedDict(zip(columns, row)) for row in cursor.fetchall()]

    def fetch_raw_data(self, sql):
        with connections['default'].cursor() as cursor:
            try:
                cursor.execute(sql)
            except Exception as err:
                data = [{'error': str(err)}]
            else:
                data = self.list_fetch_all(cursor)
        return data

    def v_progs_detailles_complet(self):
        """
        Vue postgres retournant la vue détaillant les programmes
        Les donnée sont ordonnées selon la variable self.columns
        """

        sql = """SELECT * FROM public.v_progs_detailles_complet;
        """
        return self.fetch_raw_data(sql)

    # def download_csv(self, data, fieldnames):
    #     response = HttpResponse(content_type='text/csv', charset='cp1252')
    #     response['Content-Disposition'] = "attachment; filename={}.csv".format(gen_cdc())
    #     writer = csv.DictWriter(response, fieldnames, delimiter=';')
    #     writer.writeheader()
    #     writer.writerows(data)
    #
    #     return response

    def availables_choices(self, dataset, context={}):
        intitules_programme = set(row.get('intitule_programme') for row in dataset)
        prog_choices = TProgramme.objects.filter(int_progr__in=intitules_programme).values('id_progr', 'int_progr')
        context['programmes'] = prog_choices

        moas = set(row.get('id_org_moa_id') for row in dataset)
        moa_choices = TMoa.objects.filter(id_org_moa_id__in=moas).values('id_org_moa_id', 'dim_org_moa')
        context['org_moas'] = moa_choices

        axes = set(row.get('numero_axe') for row in dataset)
        axe_choices = TAxe.objects.filter(num_axe__in=axes).values('id_axe', 'num_axe', 'int_axe', 'id_progr')
        context['axes'] = axe_choices

        sous_axes = set(row.get('numero_sous_axe') for row in dataset)
        sous_axe_choices = TSousAxe.objects.filter(num_ss_axe__in=sous_axes).values('id_ss_axe', 'num_ss_axe', 'int_ss_axe', 'id_axe')
        context['sous_axes'] = sous_axe_choices
        return context

    def get(self, request, *args, **kwargs):

        dataset = self.v_progs_detailles_complet()
        # action = request.GET.get('action')

        # if action == 'exporter-csv':
        #     data_to_export = request.session.get('v_progs_detailles_complet', dataset)
        #     return self.download_csv(data_to_export, fieldnames=dataset[0].keys())

        context = {}
        context = self.availables_choices(dataset)
        context['title'] = 'Réalisation d\'états - État d\'avancement d\'un programme' # Contenu de la balise <title/>
        context['v_progs_detailles_complet_keys'] = dataset[0].keys()
        context['v_progs_detailles_complet'] = dataset

        for key in ["id_progr", "sel_axe", "sel_ss_axe", "org_moa"]:
            context[key] = None

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        context = {}
        dataset = self.v_progs_detailles_complet()
        context = self.availables_choices(dataset)
        context['title'] = 'Réalisation d\'états - État d\'avancement d\'un programme' # Contenu de la balise <title/>
        context['v_progs_detailles_complet'] = dataset
        context['v_progs_detailles_complet_keys'] = dataset[0].keys()

        id_progr = request.POST.get('AvancementProgramme-id_progr')
        id_axe = request.POST.get('AvancementProgramme-zl_axe')
        id_ss_axe = request.POST.get('AvancementProgramme-zl_ss_axe')
        org_moa = request.POST.getlist('AvancementProgramme-cbsm_org_moa')

        axe = None
        if id_axe and id_axe != 'all':
            axe = TAxe.objects.get(id_axe=id_axe)

        ss_axe = None
        if id_ss_axe and id_ss_axe != 'all':
            ss_axe = TSousAxe.objects.get(id_ss_axe=id_ss_axe)

        if id_progr and id_progr != "all":
            dataset_prog = [row for row in dataset if row.get('id_progr_id') == int(id_progr)]
            context['v_progs_detailles_complet'] = dataset_prog

            if id_axe and id_axe != "all":
                dataset_axe = [row for row in dataset_prog if row.get('numero_axe') == int(axe.num_axe)]
                context['v_progs_detailles_complet'] = dataset_axe

                if id_ss_axe and id_ss_axe != "all":
                    dataset_ss_axe = [row for row in dataset_axe if row.get('numero_sous_axe') == int(ss_axe.num_ss_axe)]
                    context['v_progs_detailles_complet'] = dataset_ss_axe

        if org_moa:
            ds = context['v_progs_detailles_complet']
            dataset_moa = [row for row in ds if row.get('id_org_moa_id') in [int(id) for id in org_moa]]
            context['v_progs_detailles_complet'] = dataset_moa

        # moche mais permet de recuperer les valeurs apres filtre
        context["id_progr"] = id_progr
        context["sel_axe"] = axe
        context["sel_ss_axe"] = ss_axe

        context["org_moa"] = org_moa

        return render(request, self.template_name, context=context)
