import random
import re
from collections import defaultdict

# Skiplist node for information retrieval
class SkipListNode:
    def __init__(self, key, level):
        self.key = key
        self.forward = [None] * (level + 1)
        self.value = set()  # Documents containing this word

class SkipList:
    def __init__(self, max_level=16, probability=0.5):
        self.max_level = max_level
        self.probability = probability
        self.header = SkipListNode(None, max_level)
        self.level = 0

    def random_level(self):
        level = 0
        while random.random() < self.probability and level < self.max_level:
            level += 1
        return level

    def insert_word(self, word, document):
        """Insert a word with its document"""
        update = [None] * (self.max_level + 1)
        current = self.header
        
        # Find position
        for i in range(self.level, -1, -1):
            while current.forward[i] is not None and current.forward[i].key < word:
                current = current.forward[i]
            update[i] = current
        
        current = current.forward[0]
        
        # Word already exists
        if current is not None and current.key == word:
            current.value.add(document)
            return
        
        # Create new node
        new_level = self.random_level()
        if new_level > self.level:
            for i in range(self.level + 1, new_level + 1):
                update[i] = self.header
            self.level = new_level
        
        new_node = SkipListNode(word, new_level)
        new_node.value.add(document)
        
        for i in range(new_level + 1):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

    def search_word(self, word):
        """Search for a word in the skiplist"""
        current = self.header
        
        # Find the word
        for i in range(self.level, -1, -1):
            while current.forward[i] is not None and current.forward[i].key < word:
                current = current.forward[i]
        
        current = current.forward[0]
        
        if current is not None and current.key == word:
            return list(current.value)
        return []

    def range_search(self, start_word, end_word):
        """Search for words in a range"""
        current = self.header
        results = []
        
        # Find start position
        for i in range(self.level, -1, -1):
            while current.forward[i] is not None and current.forward[i].key < start_word:
                current = current.forward[i]
        
        current = current.forward[0]
        
        # Collect all words in range
        while current is not None and current.key <= end_word:
            if current.key >= start_word:
                results.extend(current.value)
            current = current.forward[0]
        
        return list(set(results))


class InformationRetrievalSystem:
    def __init__(self, filename):
        self.skiplist = SkipList()
        self.documents = {}  # {doc_id: doc_name}
        self.load_documents(filename)

    def load_documents(self, filename):
        """Load documents from file and build skiplist index"""
        try:
            print(f"\n📂 Opening file: {filename}")
            with open(filename, 'r', encoding='utf-8') as file:
                doc_id = 0
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Split by tab: title and content
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        doc_name = parts[0].strip()
                        content = parts[1].strip()
                    else:
                        doc_name = f"Doc_{doc_id}"
                        content = line
                    
                    self.documents[doc_id] = doc_name
                    print(f"  [Document {doc_id}] Loading: {doc_name[:50]}...")
                    
                    # Index all words from this document
                    # No preprocessing: just split by whitespace and convert to lowercase
                    words = content.lower().split()
                    print(f"    → Found {len(words)} words to index")
                    
                    indexed_words = set()
                    for word in words:
                        # Remove punctuation but keep word
                        clean_word = re.sub(r'[^a-z0-9]', '', word)
                        if clean_word:  # Only add non-empty words
                            self.skiplist.insert_word(clean_word, doc_id)
                            indexed_words.add(clean_word)
                    
                    print(f"    → Successfully indexed {len(indexed_words)} unique words")
                    doc_id += 1
                
                print(f"\n✓ Loading Complete!")
                print(f"✓ Total documents loaded: {doc_id}")
                print(f"✓ Index ready for searching!\n")
        
        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found!")

    def search(self, query):
        """Search for a query (single word or multiple words)"""
        print(f"\n🔍 Searching skiplist index...")
        
        # Split query into words
        query_words = query.lower().split()
        print(f"   Query words: {query_words}")
        
        all_results = None
        
        for word in query_words:
            # Clean word
            clean_word = re.sub(r'[^a-z0-9]', '', word)
            if not clean_word:
                continue
            
            print(f"\n   └─ Searching for word: '{clean_word}'")
            
            # Search in skiplist
            docs = self.skiplist.search_word(clean_word)
            print(f"      Found in {len(docs)} document(s): {docs}")
            
            if all_results is None:
                all_results = set(docs)
                print(f"      → Setting as initial result set")
            else:
                old_count = len(all_results)
                all_results = all_results.intersection(set(docs))
                print(f"      → Filtering: {old_count} → {len(all_results)} documents")
        
        # Return results
        if all_results is None:
            print(f"\n   ❌ No matches found")
            return []
        
        final_results = sorted(list(all_results))
        print(f"\n   ✓ Final result: {len(final_results)} document(s)\n")
        return final_results

    def display_results(self, query):
        """Display search results"""
        print(f"\n{'='*70}")
        print(f"📝 USER QUERY: '{query}'")
        print(f"{'='*70}")
        
        doc_ids = self.search(query)
        
        print(f"{'='*70}")
        if not doc_ids:
            print("❌ No documents found containing the query term(s).")
        else:
            print(f"✅ RESULTS: Found in {len(doc_ids)} document(s)\n")
            for idx, doc_id in enumerate(doc_ids, 1):
                doc_name = self.documents[doc_id]
                print(f"   {idx}. 📄 {doc_name}")
        
        print(f"{'='*70}\n")


# Main program
if __name__ == "__main__":
    # Initialize the information retrieval system
    print("\n" + "🚀"*35)
    print("  INFORMATION RETRIEVAL SYSTEM (Skiplist-Based)")
    print("🚀"*35)
    
    filename = "movies2.txt"
    print(f"\n⏳ Initializing system...")
    print(f"📋 Building skiplist index from '{filename}'...")
    
    ir_system = InformationRetrievalSystem(filename)
    
    # Interactive search
    print("\n" + "="*70)
    print("✅ SYSTEM READY FOR QUERIES")
    print("="*70)
    print("\n📌 HOW TO USE:")
    print("   1. Type any word (e.g., 'batman', 'prison', 'director')")
    print("   2. Type multiple words for AND search (e.g., 'batman joker')")
    print("   3. Type 'quit' to exit")
    print("   4. Type 'help' for more info")
    print("\n" + "="*70 + "\n")
    
    while True:
        try:
            query = input("🔎 Enter search query (or 'quit'/'help'): ").strip()
            
            if query.lower() == 'quit':
                print("\n👋 Thank you for using our system. Goodbye!")
                break
            
            if query.lower() == 'help':
                print("\n" + "="*70)
                print("📚 HELP - How This System Works:")
                print("="*70)
                print("\n1️⃣  INDEXING (when program starts):")
                print("    • Reads each document from movies2.txt")
                print("    • Converts all words to lowercase (NO preprocessing)")
                print("    • Stores each word in a SKIPLIST data structure")
                print("    • Maps each word to the documents containing it")
                
                print("\n2️⃣  SEARCHING (when you enter a query):")
                print("    • Splits your query into individual words")
                print("    • Looks up each word in the skiplist (fast! O(log n))")
                print("    • For multiple words, finds documents with ALL words")
                print("    • Returns matching document names")
                
                print("\n3️⃣  WHY SKIPLIST?")
                print("    • Faster than linear search (O(log n) vs O(n))")
                print("    • Like 'sorted linked list with shortcuts'")
                print("    • Easier than balanced trees for IR systems")
                
                print("\n💡 EXAMPLES:")
                print("    • 'batman'     → All movies with 'batman'")
                print("    • 'dark'       → All movies with 'dark'")
                print("    • 'batman dark' → Movies with BOTH 'batman' AND 'dark'")
                print("="*70 + "\n")
                continue
            
            if not query:
                print("⚠️  Please enter a valid query.\n")
                continue
            
            ir_system.display_results(query)
        
        except KeyboardInterrupt:
            print("\n\n👋 System interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")









