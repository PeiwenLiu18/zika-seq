#!/bin/bash -x
set -e

ref=$1
sample=$2
amplicons=$3
lib=$4
raw=$5
basecalled_reads=$6

if [[ -z "$(which sbatch)" ]]
then
  CLUSTER=0
else
  CLUSTER=1
fi

# Takes a $sample.fasta file full of nanopolish reads, ie
# nanopolish extract --type 2d /data > $sample.fasta
# Files are written to working directory

# 1) index the ref & align with bwa
bwa index $ref
bwa mem $ref $sample.fasta | samtools view -bS - | samtools sort -o $sample.sorted.bam -
samtools index $sample.sorted.bam

# 2) trim the alignments to the primer start sites and normalise the coverage to save time
python pipeline/scripts/align_trim.py --normalise 500 --start $amplicons --report $sample.alignreport.txt < $sample.sorted.bam 2> $sample.alignreport.er | samtools view -bS - | samtools sort -T $sample - -o $sample.trimmed.sorted.bam
# python pipeline/scripts/align_trim.py --normalise 100 $amplicons --report $sample.alignreport.txt < $sample.sorted.bam 2> $sample.alignreport.er | samtools view -bS - | samtools sort -T $sample - -o $sample.primertrimmed.sorted.bam
samtools index $sample.trimmed.sorted.bam
# samtools index $sample.primertrimmed.sorted.bam

# 3) do variant calling using the raw signal alignment
if [[ "${CLUSTER}" -eq "1" ]]
then
  $EBROOTNANOPOLISH/nanopolish variants --progress -t 16 --reads $sample.fasta -o $sample.vcf -b $sample.trimmed.sorted.bam -g $ref -vv -w "`pipeline/scripts/nanopolish_header.py $ref`" --snps --ploidy 1
else
  # source activate zika-seq_nanopolish &> /dev/null
  nanopolish index -d $raw -s $basecalled_reads/sequencing_summary.txt $sample.fastq
  #nanopolish index -d $raw $sample.fastq
  nanopolish variants --progress -t 16 --reads $sample.fastq -o $sample.vcf -b $sample.trimmed.sorted.bam -g $ref -vv -w "`pipeline/scripts/nanopolish_header.py $ref`" --snps --ploidy 1
  source activate zika-seq_pipeline &> /dev/null
fi

# 4) filter the variants and produce a consensus
python pipeline/scripts/margin_cons.py $ref $sample.vcf $sample.trimmed.sorted.bam a > $sample.consensus.fasta
