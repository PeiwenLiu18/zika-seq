#!/usr/bin/env python
import argparse, csv, subprocess, time
from Bio import SeqIO
import os

def sample_to_run_data_mapping(samples_dir):
    '''
    return dict
    each key is string "sample_id"
    each value is a list of tuples ("library", "barcode")
    '''
    runs_file = samples_dir + "runs.tsv"
    sr_mapping = {}
    with open(runs_file) as tsv:
        for row in csv.DictReader(tsv, delimiter="\t"):
            sample = row["sample_id"]
            rb_pair = (row["run_name"], row["barcode_id"])
            if sample not in sr_mapping:
                sr_mapping[sample] = []
            sr_mapping[sample].append(rb_pair)
    return sr_mapping

def sample_to_metadata_mapping(samples_dir):
    '''
    return dict
    each key is string "sample_id"
    each value is a list of metadata ordered as
    ["strain", "sample_id", "collect_date", "country", "division", "location"]
    '''
    metadata_file = samples_dir + "samples.tsv"
    sm_mapping = {}
    with open(metadata_file) as tsv:
        for row in csv.DictReader(tsv, delimiter="\t"):
            sample = row["sample_id"]
            metadata = [row["strain"], row["sample_id"], row["collection_date"],
                row["country"], row["division"], row["location"]]
            sm_mapping[sample] = metadata
    return sm_mapping

def construct_sample_fastas(sr_mapping, data_dir, build_dir, logfile, dimension):
    '''
    Use nanopolish to construct a single fasta for all reads from a sample
    '''
    # Pass reads
    for sample in sr_mapping:
        print("* Extracting " + sample)
        # nanopolish extract each run/barcode pair
        for (run, barcode) in sr_mapping[sample]:
            input_dir = data_dir + run + "/basecalled_reads/workspace/" + barcode # Update this to /basecalled_reads/workspace/
            print('################\n')
            print(input_dir)
            print('################\n')
            print("")
            output_file = build_dir + sample + "_" + run + "_" + barcode + ".fasta"
            f = open(output_file, "w")
            if output_file not in os.listdir(build_dir):
                if dimension == '2d':
                    call = ['$EBROOTNANOPOLISH/nanopolish', 'extract', '%s/'%(input_dir)]
                elif dimension == '1d':
                    call = ['$EBROOTNANOPOLISH/nanopolish', 'extract', '%s/'%(input_dir)]
                print(" ".join(call) + " > " + output_file)
                subprocess.call(" ".join(call), shell=True, stdout=f)
            else:
                with open(logfile, 'a') as f:
                    f.write(time.strftime('[%H:%M:%S] ' + output_file  + ' already in ' + build_dir + '\n'))

        # concatenate to single sample fasta
        input_file_list = [build_dir + sample + "_" + run + "_" + barcode + ".fasta"
            for (run, barcode) in sr_mapping[sample]]
        output_file = build_dir + sample + ".fasta"
        f = open(output_file, "w")
        call = ['cat'] + input_file_list
        # Check if any files exist to prevent freezing
        if len(input_file_list) >= 1:
            print(" ".join(call) + " > " + output_file )
            subprocess.call(call, stdout=f)
            with open(logfile, 'a') as f:
                f.write(time.strftime('[%H:%M:%S] Done writing complete fasta for ' + sample + '\n'))
        else:
            with open(logfile, 'a') as f:
                f.write("Unable to cat, no fasta files available for " + sample)
        print("")

def process_sample_fastas(sm_mapping, build_dir, logfile, dimension):
    '''
    Run fasta_to_consensus script to construct consensus files
    '''
    for sample in sm_mapping:
        print("* Processing " + sample)
        # build consensus
        sample_stem = build_dir + sample
        if dimension == '2d':
            call = ['pipeline/scripts/fasta_to_consensus_2d.sh', '/fh/fast/bedford_t/zika-seq/pipeline/refs/KJ776791.2.fasta', sample_stem, '/fh/fast/bedford_t/zika-seq/pipeline/metadata/v2_500.amplicons.ver2.bed']
        elif dimension == '1d':
            call = ['pipeline/scripts/fasta_to_consensus_1d.sh', '/fh/fast/bedford_t/zika-seq/pipeline/refs/KJ776791.2.fasta', sample_stem, '/fh/fast/bedford_t/zika-seq/pipeline/metadata/v2_500.amplicons.ver2.bed']
        print(" ".join(call))
        subprocess.call(call)
        # annotate consensus
        # >ZBRD116|ZBRD116|2015-08-28|brazil|alagoas|arapiraca|minion
        print('#############\n')
        fasta_header = ">" + "|".join(sm_mapping[sample])
        fasta_header += "|minion"
        replacement = r"\~^>~s~.*~" + fasta_header + "~" # ~ rather than / to avoid conflict with strain names
        input_file = build_dir + sample + ".consensus.fasta"
        output_file = "temp.fasta"
        f = open(output_file, "w")
        call = ['sed', replacement, input_file]
        print(" ".join(call) + " > " + output_file)
        subprocess.call(call, stdout=f)
        call = ['mv', output_file, input_file]
        print(" ".join(call))
        subprocess.call(call)
        with open(logfile, 'a') as f:
            f.write(time.strftime('[%H:%M:%S] Consensus fasta completed for ' + sample + '\n'))
        print("")

def gather_consensus_fastas(sm_mapping, build_dir, prefix, logfile):
    '''
    Gather consensus files into genomes with 'partial' (50-80% coverage)
    and good (>80% coverage) coverage
    '''
    # identify partial and good samples
    print("* Concatenating consensus fastas")
    partial_samples = []
    good_samples = []
    poor_samples = []
    for sample in sm_mapping:
        consensus_file = build_dir + sample + ".consensus.fasta"
        with open(consensus_file) as f:
            lines = f.readlines()
        seq = lines[1]
        coverage = 1 - seq.count("N") / float(len(seq))
        print(seq.count("N")) #DEBUG
        print(len(seq)) #DEBUG
        print("COVERAGE: "+ str(coverage)) #DEBUG
        if coverage >= 0.5 and coverage < 0.8:
            partial_samples.append(sample)
        elif coverage >= 0.8:
            good_samples.append(sample)
        else:
            poor_samples.append(sample)
    # sort samples
    partial_samples.sort()
    good_samples.sort()
    poor_samples.sort()
    print("Good samples: " + " ".join(good_samples))
    print("Partial samples: " + " ".join(partial_samples))
    print("Poor samples: " + " ".join(poor_samples))
    input_file_list = [build_dir + sample + ".consensus.fasta" for sample in partial_samples]
    output_file = build_dir + prefix + "_partial.fasta"
    f = open(output_file, "w")
    call = ['cat'] + input_file_list
    print(" ".join(call) + " > " + output_file)
    if len(input_file_list) >= 1:
        subprocess.call(call, stdout=f)
    # concatenate good samples
    input_file_list = [build_dir + sample + ".consensus.fasta" for sample in good_samples]
    output_file = build_dir + prefix + "_good.fasta"
    f = open(output_file, "w")
    call = ['cat'] + input_file_list
    print(" ".join(call) + " > " + output_file)
    subprocess.call(call, stdout=f)
    # concatenate poor samples
    print("Poor samples: " + " ".join(good_samples))
    input_file_list = [build_dir + sample + ".consensus.fasta" for sample in poor_samples]
    output_file = build_dir + prefix + "_poor.fasta"
    f = open(output_file, "w")
    call = ['cat'] + input_file_list
    print(" ".join(call) + " > " + output_file)
    subprocess.call(call, stdout=f)
    with open(logfile, 'a') as f:
        f.write(time.strftime('[%H:%M:%S] Done gathering consensus fastas\n'))
    print("")

def overlap(sr_mapping, build_dir, logfile):
    # prepare sorted bam files for coverage plots
    for sample in sr_mapping:
        # samtools depth <name.sorted.bam> > <name.coverage>
        bamfile = build_dir + sample + '.sorted.bam'
        coveragefile = build_dir + sample + '.coverage'
        with open(coveragefile, 'w+') as f:
            call = ['samtools', 'depth', bamfile]
            print(" ".join(call + ['>', coveragefile]))
            subprocess.call(call, stdout=f)

        chfile = build_dir + sample + '.chr1.coverage'
        with open(coveragefile, 'r') as f:
            f.readline()
            line = f.readline()
            l = line.split('\t')
            chromosome_name = l[0]
        call = "awk '$1 == \"" + chromosome_name + "\" {print $0}' " + coveragefile + " > " + chfile
        print(call)
        subprocess.call([call], shell=True)
        call = "Rscript /fh/fast/bedford_t/zika-seq/pipeline/scripts/depth_coverage.R --inFile " + chfile + " --outPath " + build_dir + " --name " + sample
        print(call)
        subprocess.call([call], shell=True)
        print("")
        with open(logfile, 'a') as f:
            f.write(time.strftime('[%H:%M:%S] Done drawing overlap graphs for ' + sample + '\n'))

def per_base_error_rate(sr_mapping, build_dir, logfile):
    '''
    Calculate per-base error rates by walking through VCF files for each sample.
    TODO: make this work
    '''
    length = 10794.0 # TODO: Make sure this always works or is variable
    for sample in sr_mapping:
        error = 0
        vcf = build_dir + sample + '.vcf'
        if vcf in os.listdir(build_dir):
            with open(vcf) as f:
                lines = f.readlines()
                if len(lines) > 1:
                    for line in lines:
                        l = line.split('\t')
                        alt = len(l[4])
                        error += alt
            outfile = build_dir + sample + '.error'
            error = error / length
            with open(outfile, 'w+') as f:
                f.write('Error rate: ' + str(error))
    with open(logfile, 'a') as f:
        f.write(time.strftime('[%H:%M:%S] Done calculating per-base error rates ' + sample + '\n'))

if __name__=="__main__":
    parser = argparse.ArgumentParser( description = "process data" )
    parser.add_argument( '--data_dir', type = str, default = "/fh/fast/bedford_t/zika-seq/data/",
                            help="directory containing data; default is \'/fh/fast/bedford_t/zika-seq/data/\'")
    parser.add_argument( '--samples_dir', type = str, default = "/fh/fast/bedford_t/zika-seq/samples/",
                            help="directory containing samples and runs TSVs; default is \'/fh/fast/bedford_t/zika-seq/samples/\'" )
    parser.add_argument( '--build_dir', type = str, default = "/fh/fast/bedford_t/zika-seq/build/",
                            help="directory for output data; default is \'/fh/fast/bedford_t/zika-seq/build/\'" )
    parser.add_argument('--prefix', type = str, default = "ZIKA_USVI",
                            help="string to be prepended onto all output consensus genome files; default is \'ZIKA_USVI\'")
    parser.add_argument('--samples', type = str, nargs='*', default = None,
                            help="sample(s) to be run; if blank, default is all samples listed in runs.tsv")
    parser.add_argument('--dimension', type = str, default = '2d',
                            help="dimension of library to be fun; options are \'1d\' or \'2d\', default is \'2d\'")
    params = parser.parse_args()

    assert params.dimension in [ '1d', '2d' ], "Unknown library dimension: options are \'1d\' or \'2d\'."

    logfile = params.build_dir + 'log.txt'
    start_time = time.time()
    with open(logfile,'w+') as f:
        f.write(time.strftime('Pipeline started on %Y-%m-%d at %H:%M:%S\n'))

    sr_mapping = sample_to_run_data_mapping(params.samples_dir)
    sm_mapping = sample_to_metadata_mapping(params.samples_dir)
    tmp_sr = { s: sr_mapping[s] for s in params.samples }
    tmp_sm = { s: sm_mapping[s] for s in params.samples }
    sr_mapping = tmp_sr
    sm_mapping = tmp_sm

    with open(logfile,'a') as f:
        f.write('Samples:\n')
        for sample in sr_mapping:
            f.write(sample+'\n')
            for (run, barcode) in sr_mapping[sample]:
                f.write('\t('+run+', '+barcode+')\n')

    construct_sample_fastas(sr_mapping, params.data_dir, params.build_dir, logfile, params.dimension)
    process_sample_fastas(sm_mapping, params.build_dir, logfile, params.dimension)
    gather_consensus_fastas(sm_mapping, params.build_dir, params.prefix, logfile)
    overlap(sm_mapping, params.build_dir, logfile)
    per_base_error_rate(sr_mapping, params.build_dir, logfile)

    time_elapsed = time.time() - start_time
    m, s = divmod(time_elapsed, 60)
    h, m = divmod(m, 60)
    with open(logfile,'a') as f:
        f.write(time.strftime('Pipeline completed on %Y-%m-%d at %H:%M:%S\n'))
        f.write('Total runtime: %d:%02d:%02d' % (h, m, s))
