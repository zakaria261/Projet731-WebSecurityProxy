"""
Script de test du proxy sur différents sites web
Teste la compatibilité et mesure les performances
"""

import requests
import time
from statistics import mean, stdev

PROXY = {
    'http': 'http://127.0.0.1:8080',
}

TEST_SITES = [
    'http://neverssl.com',
    'http://example.com',
    'http://info.cern.ch',
    'http://httpforever.com',
    'http://www.columbia.edu',
]

def test_site_connectivity(url, use_proxy=True):
    """Teste si un site est accessible via le proxy"""
    try:
        proxies = PROXY if use_proxy else None
        response = requests.get(url, proxies=proxies, timeout=10)
        return {
            'success': True,
            'status_code': response.status_code,
            'content_length': len(response.content),
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'status_code': None,
            'content_length': 0,
            'error': str(e)
        }

def measure_latency(url, iterations=5):
    """Mesure le délai moyen pour accéder à un site"""
    latencies_with_proxy = []
    latencies_without_proxy = []
    
    print(f"\n{'='*60}")
    print(f"Test de latence pour : {url}")
    print(f"{'='*60}")
    
    for i in range(iterations):
        start = time.time()
        result = test_site_connectivity(url, use_proxy=True)
        end = time.time()
        
        if result['success']:
            latency = (end - start) * 1000  # en millisecondes
            latencies_with_proxy.append(latency)
            print(f"  Avec proxy - Essai {i+1}: {latency:.2f} ms")
        else:
            print(f"  Avec proxy - Essai {i+1}: ÉCHEC - {result['error']}")
    
  
    print(f"\n  Connexion directe (référence):")
    for i in range(iterations):
        start = time.time()
        result = test_site_connectivity(url, use_proxy=False)
        end = time.time()
        
        if result['success']:
            latency = (end - start) * 1000
            latencies_without_proxy.append(latency)
            print(f"  Sans proxy - Essai {i+1}: {latency:.2f} ms")
    
    # Calcul des statistiques
    if latencies_with_proxy and latencies_without_proxy:
        avg_with = mean(latencies_with_proxy)
        avg_without = mean(latencies_without_proxy)
        overhead = avg_with - avg_without
        overhead_percent = (overhead / avg_without) * 100
        
        print(f"\n RÉSULTATS:")
        print(f"     Latence moyenne AVEC proxy    : {avg_with:.2f} ms")
        print(f"     Latence moyenne SANS proxy    : {avg_without:.2f} ms")
        print(f"     Surcoût (overhead)            : {overhead:.2f} ms ({overhead_percent:.1f}%)")
        
        if len(latencies_with_proxy) > 1:
            print(f"     Écart-type avec proxy         : {stdev(latencies_with_proxy):.2f} ms")
        
        return {
            'avg_with_proxy': avg_with,
            'avg_without_proxy': avg_without,
            'overhead_ms': overhead,
            'overhead_percent': overhead_percent
        }
    
    return None

def measure_throughput(url, iterations=3):
    """Mesure le débit en téléchargeant du contenu"""
    print(f"\n{'='*60}")
    print(f"Test de débit pour : {url}")
    print(f"{'='*60}")
    
    throughputs_with_proxy = []
    throughputs_without_proxy = []
    

    for i in range(iterations):
        try:
            start = time.time()
            response = requests.get(url, proxies=PROXY, timeout=10)
            end = time.time()
            
            duration = end - start
            size_mb = len(response.content) / (1024 * 1024)
            throughput = size_mb / duration  # MB/s
            throughputs_with_proxy.append(throughput)
            
            print(f"  Avec proxy - Essai {i+1}: {size_mb:.3f} MB en {duration:.2f}s = {throughput:.2f} MB/s")
        except Exception as e:
            print(f"  Avec proxy - Essai {i+1}: ÉCHEC - {e}")
    
   
    print(f"\n  Connexion directe (référence):")
    for i in range(iterations):
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            end = time.time()
            
            duration = end - start
            size_mb = len(response.content) / (1024 * 1024)
            throughput = size_mb / duration
            throughputs_without_proxy.append(throughput)
            
            print(f"  Sans proxy - Essai {i+1}: {size_mb:.3f} MB en {duration:.2f}s = {throughput:.2f} MB/s")
        except Exception as e:
            print(f"  Sans proxy - Essai {i+1}: ÉCHEC - {e}")
    
    if throughputs_with_proxy and throughputs_without_proxy:
        avg_with = mean(throughputs_with_proxy)
        avg_without = mean(throughputs_without_proxy)
        degradation = ((avg_without - avg_with) / avg_without) * 100
        
        print(f"\n   RÉSULTATS:")
        print(f"     Débit moyen AVEC proxy  : {avg_with:.2f} MB/s")
        print(f"     Débit moyen SANS proxy  : {avg_without:.2f} MB/s")
        print(f"     Dégradation             : {degradation:.1f}%")
        
        return {
            'throughput_with_proxy': avg_with,
            'throughput_without_proxy': avg_without,
            'degradation_percent': degradation
        }
    
    return None

def run_full_test_suite():
    """Exécute la suite complète de tests"""
    print("\n" + "="*60)
    print(" TEST DU PROXY DE SÉCURITÉ WEB")
    print("="*60)
    
    print("\n\n TEST 1: CONNECTIVITÉ DES SITES")
    print("="*60)
    
    success_count = 0
    for site in TEST_SITES:
        result = test_site_connectivity(site, use_proxy=True)
        status = " OK" if result['success'] else " ÉCHEC"
        print(f"{status} {site}")
        if result['success']:
            print(f"    Status: {result['status_code']}, Taille: {result['content_length']} octets")
            success_count += 1
        else:
            print(f"    Erreur: {result['error']}")
    
    print(f"\n Taux de succès: {success_count}/{len(TEST_SITES)} ({(success_count/len(TEST_SITES)*100):.1f}%)")
    
    
    print("\n\n  TEST 2: MESURE DE LATENCE")
    latency_results = []
    for site in TEST_SITES[:3]:  
        result = measure_latency(site, iterations=5)
        if result:
            latency_results.append(result)
    
    
    print("\n\n TEST 3: MESURE DE DÉBIT")
    throughput_results = []
    for site in TEST_SITES[:2]:  
        result = measure_throughput(site, iterations=3)
        if result:
            throughput_results.append(result)
    
    
    print("\n\n" + "="*60)
    print(" RÉSUMÉ GLOBAL DES PERFORMANCES")
    print("="*60)
    
    if latency_results:
        avg_overhead = mean([r['overhead_ms'] for r in latency_results])
        avg_overhead_percent = mean([r['overhead_percent'] for r in latency_results])
        print(f"\n LATENCE:")
        print(f"   Surcoût moyen du chiffrement : {avg_overhead:.2f} ms ({avg_overhead_percent:.1f}%)")
    
    if throughput_results:
        avg_degradation = mean([r['degradation_percent'] for r in throughput_results])
        print(f"\n DÉBIT:")
        print(f"   Dégradation moyenne          : {avg_degradation:.1f}%")
    
    print("\n" + "="*60)
    print(" Tests terminés !")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("  Assurez-vous que les deux proxies sont démarrés :")
    print("   Terminal 1: python -m web_security_proxy.proxy_destination.server_proxy")
    print("   Terminal 2: python -m web_security_proxy.proxy_source.client_proxy")
    input("\nAppuyez sur Entrée pour commencer les tests...")
    
    run_full_test_suite()
