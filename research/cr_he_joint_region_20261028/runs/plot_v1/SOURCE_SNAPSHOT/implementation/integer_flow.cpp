// Exact integer Dinic backend for BASS_CR_INTEGER_FLOW_V1.
// Build under the caller's ledger: g++ -std=c++17 -O2 integer_flow.cpp -o integer_flow
// No floating capacities, recursion, worker threads, or external libraries.

#include <algorithm>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Int = __int128_t;
using UInt = __uint128_t;
static constexpr UInt CAPACITY_LIMIT = UInt(1) << 126;
static const char* PROTOCOL = "BASS_CR_INTEGER_FLOW_V1";

static std::string token(const char* label) {
    std::string value;
    if (!(std::cin >> value)) {
        throw std::invalid_argument(std::string("MISSING_TOKEN:") + label);
    }
    return value;
}

static Int decimal(const std::string& text, const char* label) {
    if (text.empty()) {
        throw std::invalid_argument(std::string("EMPTY_INTEGER:") + label);
    }
    UInt value = 0;
    for (char c : text) {
        if (c < '0' || c > '9') {
            throw std::invalid_argument(std::string("NONNEGATIVE_DECIMAL_REQUIRED:") + label);
        }
        const unsigned digit = static_cast<unsigned>(c - '0');
        if (value > (CAPACITY_LIMIT - 1 - digit) / 10) {
            throw std::overflow_error(std::string("INTEGER_MUST_BE_BELOW_2_POW_126:") + label);
        }
        value = value * 10 + digit;
    }
    return static_cast<Int>(value);
}

static int small_integer(const char* label) {
    const Int value = decimal(token(label), label);
    if (value > std::numeric_limits<int>::max()) {
        throw std::overflow_error(std::string("INDEX_OUTSIDE_INT_RANGE:") + label);
    }
    return static_cast<int>(value);
}

static std::string decimal_text(Int value) {
    if (value < 0) {
        throw std::logic_error("NEGATIVE_OUTPUT_INTEGER");
    }
    if (value == 0) {
        return "0";
    }
    std::string out;
    while (value != 0) {
        out.push_back(static_cast<char>('0' + static_cast<int>(value % 10)));
        value /= 10;
    }
    std::reverse(out.begin(), out.end());
    return out;
}

struct Edge {
    int to;
    Int capacity;
};

class Network {
public:
    std::vector<std::vector<int>> adjacency;
    std::vector<Edge> edges;
    std::vector<Int> original;
    std::uint64_t phases = 0;
    Int augmentations = 0;

    Network(int nodes, int edge_count) : adjacency(static_cast<std::size_t>(nodes)) {
        edges.reserve(static_cast<std::size_t>(edge_count) * 2);
        original.reserve(static_cast<std::size_t>(edge_count));
    }

    void add(int from, int to, Int capacity) {
        const int index = static_cast<int>(edges.size());
        adjacency[from].push_back(index);
        edges.push_back(Edge{to, capacity});
        adjacency[to].push_back(index + 1);
        edges.push_back(Edge{from, 0});
        original.push_back(capacity);
    }

    bool levels(int source, int sink, std::vector<int>& level) const {
        std::fill(level.begin(), level.end(), -1);
        std::queue<int> queue;
        level[source] = 0;
        queue.push(source);
        while (!queue.empty()) {
            const int vertex = queue.front();
            queue.pop();
            for (int index : adjacency[vertex]) {
                const Edge& edge = edges[index];
                if (edge.capacity > 0 && level[edge.to] < 0) {
                    level[edge.to] = level[vertex] + 1;
                    queue.push(edge.to);
                }
            }
        }
        return level[sink] >= 0;
    }

    Int augment_one(int source, int sink, Int maximum,
                    std::vector<int>& level, std::vector<std::size_t>& cursor,
                    std::vector<int>& vertices, std::vector<int>& path,
                    std::vector<Int>& bottleneck) {
        vertices.clear();
        path.clear();
        bottleneck.clear();
        vertices.push_back(source);
        bottleneck.push_back(maximum);
        while (!vertices.empty()) {
            const int vertex = vertices.back();
            if (vertex == sink) {
                const Int amount = bottleneck.back();
                if (amount <= 0) {
                    throw std::logic_error("NONPOSITIVE_AUGMENTATION");
                }
                for (int index : path) {
                    edges[index].capacity -= amount;
                    edges[index ^ 1].capacity += amount;
                }
                return amount;
            }
            bool advanced = false;
            while (cursor[vertex] < adjacency[vertex].size()) {
                const int index = adjacency[vertex][cursor[vertex]];
                const Edge& edge = edges[index];
                if (edge.capacity > 0 && level[edge.to] == level[vertex] + 1) {
                    const Int amount = std::min(bottleneck.back(), edge.capacity);
                    path.push_back(index);
                    vertices.push_back(edge.to);
                    bottleneck.push_back(amount);
                    advanced = true;
                    break;
                }
                ++cursor[vertex];
            }
            if (!advanced) {
                // Reverse residual arcs go backwards in this level graph.
                level[vertex] = -1;
                vertices.pop_back();
                bottleneck.pop_back();
                if (!path.empty()) {
                    path.pop_back();
                    ++cursor[vertices.back()];
                }
            }
        }
        return 0;
    }

    Int max_flow(int source, int sink, Int bound) {
        const std::size_t size = adjacency.size();
        std::vector<int> level(size);
        std::vector<std::size_t> cursor(size);
        std::vector<int> vertices;
        std::vector<int> path;
        std::vector<Int> bottleneck;
        vertices.reserve(size);
        path.reserve(size);
        bottleneck.reserve(size);
        Int total = 0;
        while (total < bound && levels(source, sink, level)) {
            ++phases;
            std::fill(cursor.begin(), cursor.end(), 0);
            while (total < bound) {
                const Int amount = augment_one(source, sink, bound - total,
                    level, cursor, vertices, path, bottleneck);
                if (amount == 0) {
                    break;
                }
                total += amount;
                ++augmentations;
            }
        }
        return total;
    }
};

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    try {
        if (token("PROTOCOL") != PROTOCOL) {
            throw std::invalid_argument("PROTOCOL_MISMATCH");
        }
        const int nodes = small_integer("NODES");
        const int count = small_integer("EDGES");
        const int source = small_integer("SOURCE");
        const int sink = small_integer("SINK");
        const Int bound = decimal(token("BOUND"), "BOUND");
        if (nodes < 2 || source >= nodes || sink >= nodes || source == sink) {
            throw std::invalid_argument("NODE_OR_TERMINAL_RANGE");
        }
        if (count > std::numeric_limits<int>::max() / 2) {
            throw std::overflow_error("EDGE_INDEX_RANGE");
        }
        Network network(nodes, count);
        for (int i = 0; i < count; ++i) {
            const int from = small_integer("EDGE_FROM");
            const int to = small_integer("EDGE_TO");
            const Int capacity = decimal(token("CAPACITY"), "CAPACITY");
            if (from >= nodes || to >= nodes || from == to) {
                throw std::invalid_argument("EDGE_ENDPOINT_RANGE");
            }
            network.add(from, to, capacity);
        }
        std::string extra;
        if (std::cin >> extra) {
            throw std::invalid_argument("TRAILING_INPUT");
        }
        const Int flow = network.max_flow(source, sink, bound);
        std::cout << PROTOCOL << '\n';
        std::cout << nodes << ' ' << count << ' ' << decimal_text(flow) << ' '
                  << network.phases << ' ' << decimal_text(network.augmentations) << '\n';
        for (int i = 0; i < count; ++i) {
            const Int amount = network.original[i] - network.edges[2 * i].capacity;
            if (amount < 0 || amount > network.original[i]) {
                throw std::logic_error("OUTPUT_EDGE_FLOW_RANGE");
            }
            std::cout << decimal_text(amount) << '\n';
        }
        if (!std::cout) {
            throw std::runtime_error("OUTPUT_STREAM_FAILED");
        }
        return 0;
    } catch (const std::overflow_error& error) {
        std::cerr << "OVERFLOW:" << error.what() << '\n';
        return 3;
    } catch (const std::exception& error) {
        std::cerr << "ERROR:" << error.what() << '\n';
        return 2;
    }
}
