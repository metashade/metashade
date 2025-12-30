# Copyright 2025 Pavlo Penenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tests for operator precedence and parenthesis reduction.

These tests verify that:
1. Compound expressions are properly wrapped when used as operands
2. Negation of compound expressions is handled correctly
3. Mixed precedence scenarios produce correct output
"""

from metashade.util.testing import ctx_cls_hg

class TestPrecedence:
    """Tests for mixed operator precedence scenarios."""
    
    @ctx_cls_hg
    def test_mixed_precedence(self, ctx_cls):
        """
        Test that compound expressions maintain parentheses when used
        as operands in subsequent operations.
        
        Cases:
        - (a + b) * c should keep parens
        - a * (b + c) should keep parens  
        - (a * b) + c should keep parens (for readability)
        - a + b + c chains should work correctly
        """
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('test_mixed_precedence', sh.Float)():
                sh.a = sh.Float(1.0)
                sh.b = sh.Float(2.0)
                sh.c = sh.Float(3.0)
                
                # (a + b) * c - compound addition used in multiplication
                sh.r1 = (sh.a + sh.b) * sh.c
                
                # a * (b + c) - compound addition used after multiplication
                sh.r2 = sh.a * (sh.b + sh.c)
                
                # (a * b) + c - compound multiplication used in addition
                sh.r3 = (sh.a * sh.b) + sh.c
                
                # a + (b * c) - should also keep parens for consistency
                sh.r4 = sh.a + (sh.b * sh.c)
                
                # Chained operations: a + b + c
                sh.r5 = sh.a + sh.b + sh.c
                
                # Chained with mixed operators: a + b * c (no Python parens)
                # Note: Python evaluates a + (b * c) due to precedence,
                # but we expect the generated code to reflect the structure
                sh.r6 = sh.a + sh.b * sh.c
                
                sh.return_(sh.r1)


class TestNegation:
    """Tests for negation operator with compound expressions."""
    
    @ctx_cls_hg
    def test_negation_simple(self, ctx_cls):
        """Test negation of simple variables."""
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('test_negation_simple', sh.Float)():
                sh.a = sh.Float(1.0)
                
                # Simple negation
                sh.r1 = -sh.a
                
                # Negation used in expression
                sh.r2 = -sh.a + sh.a
                
                # Negation on RHS
                sh.r3 = sh.a + (-sh.a)
                
                sh.return_(sh.r1)
    
    @ctx_cls_hg
    def test_negation_compound(self, ctx_cls):
        """
        Test negation of compound expressions.
        
        This verifies that -(a + b) correctly wraps the compound expression.
        """
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('test_negation_compound', sh.Float)():
                sh.a = sh.Float(1.0)
                sh.b = sh.Float(2.0)
                
                # Negation of a compound expression
                sh.sum_ab = sh.a + sh.b
                sh.r1 = -sh.sum_ab
                
                # Direct negation of compound (if Python allows)
                # This creates -(a + b) inline
                sh.r2 = -(sh.a + sh.b)
                
                # Negation result used in further operations
                sh.neg_sum = -sh.sum_ab
                sh.r3 = sh.neg_sum + sh.a
                sh.r4 = sh.neg_sum * sh.b
                
                # Double negation
                sh.r5 = -(-sh.a)
                
                # Double negation of compound
                sh.r6 = -(-sh.sum_ab)
                
                sh.return_(sh.r1)
    
    @ctx_cls_hg
    def test_negation_in_operations(self, ctx_cls):
        """Test negation results used as operands in binary operations."""
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('test_negation_in_ops', sh.Float)():
                sh.a = sh.Float(1.0)
                sh.b = sh.Float(2.0)
                
                # Negation result as LHS
                sh.r1 = (-sh.a) + sh.b
                sh.r2 = (-sh.a) * sh.b
                
                # Negation result as RHS
                sh.r3 = sh.a + (-sh.b)
                sh.r4 = sh.a * (-sh.b)
                
                # Chained: -a + b + c  
                sh.c = sh.Float(3.0)
                sh.r5 = -sh.a + sh.b + sh.c
                
                sh.return_(sh.r1)


class TestVectorPrecedence:
    """Tests for precedence with vector types."""
    
    @ctx_cls_hg
    def test_vector_mixed_precedence(self, ctx_cls):
        """Test mixed precedence with vector operations."""
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('test_vector_precedence', sh.Float3)():
                sh.v1 = sh.Float3((1.0, 2.0, 3.0))
                sh.v2 = sh.Float3((4.0, 5.0, 6.0))
                sh.s = sh.Float(2.0)
                
                # (v1 + v2) * s - compound vector addition scaled
                sh.r1 = (sh.v1 + sh.v2) * sh.s
                
                # v1 * s + v2 - scaled vector plus another
                sh.r2 = sh.v1 * sh.s + sh.v2
                
                # Negation of vector
                sh.r3 = -sh.v1
                
                # Negation of compound vector expression
                sh.r4 = -(sh.v1 + sh.v2)
                
                sh.return_(sh.r1)
