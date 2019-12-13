#!/usr/bin/perl
use strict;

my $file_in = $ARGV[0];
my $file_out = $ARGV[1];

if(scalar(@ARGV) != 2) {
	print "USAGE: ./xml2json.pl namefile_in namefile_out\n";
}

my $username = "";
my $content = "";
my $favoris = "";
my $retweet = "";
my $date = "";
my $compteur = 1;
my @hashtags = ();

open(IN,$file_in);
open(OUT,"> $file_out");
while(<IN>) {
	chomp;
	my $line = $_;
	$line =~ s/\t//g;
	$line =~ s/\"/\\"/g;
	$line =~ s/\\([^"])/\\\\\1/g;
	
	#recup des infos
	if($line =~ /^<username>/) {
		($username) = ($line =~ /<username>(.*)<\/username>/);
	}
	if($line =~ /^<message>/) {
		($content) = ($line =~ /<message>(.*)<\/message>/);

		#get hashtag in json format
		my @t = split(" ",$content);
		foreach my $word (@t) {
			if($word =~ /^\#/) {
				push (@hashtags,$word);
			}
		}
	}
	if($line =~ /^<favoris>/) {
		($favoris) = ($line =~ /<favoris>(.*)<\/favoris>/);
	}
	if($line =~ /^<retweet>/) {
		($retweet) = ($line =~ /<retweet>(.*)<\/retweet>/);
	}
	if($line =~ /^<date>/) {
		($date) = ($line =~ /<date>(.*)<\/date>/);
	}

	#on affiche les res
	if($line eq "</tweet>") {
		print OUT "{\"index\":{\"_id\":$compteur}}\n";
		print OUT "{\"date\":\"$date\",\"favoris\":\"$favoris\",\"message\":\"$content\",\"retweet\":\"$retweet\",\"username\":\"$username\",";
		#print all the hashtags in a tab
		my $to_print = "";
		$to_print = "\"hashtags\":[";
		foreach my $hash(@hashtags) {
			$to_print .= "{\"text\":\"$hash\"},";
		}
		#supprime la dernière virgule
		if(scalar(@hashtags) > 0){chop($to_print)};
		print OUT "$to_print]}\n";
		$compteur++;
		@hashtags = ();
	}
}
close(IN);
close(OUT);