import itertools
import os
genres_wd = r'P:\06_Tools\v_control\Models\Options'
combi_wd = r'P:\06_Tools\v_control\Models\Combinations'
baseline_wd = r'P:\06_Tools\v_control\Models\Baseline'

genres = os.listdir(genres_wd)
flavors = []
for gen in genres:
    for flav in os.listdir(os.path.join(genres_wd, gen)):
        #print os.path.join(gen, flav)
        flavors.append(os.path.join(gen, flav))

newmodels = []
basemodel = swmmio.Model(baseline_wd)
#creat directories for new model combinations
for L in range(1, len(flavors)+1):
  for subset in itertools.combinations(flavors, L):


    #newcombi = '_'.join(subset)
    newcombi = '_'.join([os.path.split(s)[1] for s in subset])
    new_combi_dir = os.path.join(combi_wd, newcombi)

    #create a list of the parent directories, use that to prevent
    #two or more from same genre
    genredirs = [os.path.split(s)[0] for s in subset]
    if len(genredirs) == len(set(genredirs)) and len(subset) > 1:
            #confirming the list length is equal to the set length (hashable)
            #confirms that there are not duplicates in the items list

        if not os.path.exists(new_combi_dir):#and newcombi not in flavors:
            #check to make sure new model doesn't repeat two or more from
            #a particular genre.
            print new_combi_dir
            os.mkdir(new_combi_dir)
            newmodels.append(new_combi_dir)

        #create the new model
        model_objects = [swmmio.Model(os.path.join(genres_wd, f)) for f in subset]
        vc.combine_models(basemodel, newdir=new_combi_dir, models=model_objects)
